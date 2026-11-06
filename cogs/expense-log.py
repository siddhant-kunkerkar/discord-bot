import io
import os
import json
import datetime
from collections import defaultdict
import pandas as pd
from dotenv import load_dotenv

import discord
from discord.ext import commands
from discord import app_commands
import gspread

from google import genai
from google.genai import types

# Use absolute paths for the VM
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.join(BASE_DIR, "..")
SETTINGS_FILE = os.path.join(ROOT_DIR, "bot_settings.json")
OPTIONS_CSV = os.path.join(ROOT_DIR, "options.csv")
CREDS_FILE = os.path.join(ROOT_DIR, "credentials.json")


def format_size(size_bytes: int) -> str:
    """Formats raw byte counts into B, KB, or MB."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    return f"{size_bytes / (1024 * 1024):.2f} MB"


class ExpenseTracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.latest_model = "gemini-3.1-flash-lite"

        # Initialize Clients
        self.ai_client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
        self.gc = gspread.service_account(filename=CREDS_FILE)
        self.workbook = self.gc.open(os.getenv('SHEET_NAME'))

        # Load context
        options_df = pd.read_csv(OPTIONS_CSV)
        self.categories = options_df['category'].dropna().tolist()
        self.payment_methods = options_df['payment_method'].dropna().tolist()
        self.expense_type = options_df['expense_type'].dropna().tolist()

    def load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r") as f:
                return json.load(f)
        return {"allowed_channels": []}

    def save_settings(self, settings):
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings, f)

    @app_commands.command(name="setup", description="Enable or disable the bot in this channel")
    @app_commands.describe(action="Choose 'enable' or 'disable'")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_slash(self, interaction: discord.Interaction, action: str):
        """Enable or disable the bot in this channel."""
        settings = self.load_settings()
        if action.lower() == "enable":
            if interaction.channel.id not in settings["allowed_channels"]:
                settings["allowed_channels"].append(interaction.channel.id)
                self.save_settings(settings)
            await interaction.response.send_message(f"✅ Bot enabled for **#{interaction.channel.name}**.")
        elif action.lower() == "disable":
            if interaction.channel.id in settings["allowed_channels"]:
                settings["allowed_channels"].remove(interaction.channel.id)
                self.save_settings(settings)
            await interaction.response.send_message(f"❌ Bot disabled for **#{interaction.channel.name}**.")

    @app_commands.command(name="expense-log", description="Log an expense from a receipt photo")
    @app_commands.describe(receipt="Upload a receipt photo directly")
    async def exp_slash(self, interaction: discord.Interaction, receipt: discord.Attachment = None):
        """Slash command to process expenses."""
        settings = self.load_settings()
        if interaction.channel.id not in settings["allowed_channels"]:
            return await interaction.response.send_message(
                "❌ This channel is not enabled. Use `/setup enable` first.",
                ephemeral=True
            )

        target_attachment = receipt
        await interaction.response.defer()

        if target_attachment:
            if target_attachment.content_type and target_attachment.content_type.startswith('image/'):
                await self.process_expense(interaction, target_attachment)
            else:
                await interaction.followup.send("⚠️ The uploaded file is not an image.")
        else:
            await interaction.followup.send("⚠️ Please upload a receipt photo while using this command.")

    async def process_expense(self, interaction, attachment):
        file_size_str = format_size(attachment.size)
        print(f"[RECEIPT] Processing {attachment.filename} ({file_size_
