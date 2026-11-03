import discord
from discord.ext import commands
from discord import app_commands
import gspread
import os
import json
import pandas as pd
import datetime
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Use absolute paths for the VM
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.join(BASE_DIR, "..")
SETTINGS_FILE = os.path.join(ROOT_DIR, "bot_settings.json")
OPTIONS_CSV = os.path.join(ROOT_DIR, "options.csv")
CREDS_FILE = os.path.join(ROOT_DIR, "credentials.json")

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

    # UPDATED: Changed to slash command to ensure sync
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
        
        # 1. Check if channel is enabled
        settings = self.load_settings()
        if interaction.channel.id not in settings["allowed_channels"]:
            return await interaction.response.send_message(
                "❌ This channel is not enabled. Use `/setup enable` first.", 
                ephemeral=True
            )

        target_attachment = receipt

        # 3. Defer response
        await interaction.response.defer()

        if target_attachment:
            if target_attachment.content_type and target_attachment.content_type.startswith('image/'):
                await self.process_expense(interaction, target_attachment)
            else:
                await interaction.followup.send("⚠️ The uploaded file is not an image.")
        else:
            await interaction.followup.send("⚠️ Please upload a receipt photo while using this command.")

    async def process_expense(self, interaction, attachment):
        status_msg = await interaction.followup.send(f"🔍 Analyzing with {self.latest_model}...")
        img_path = os.path.join(ROOT_DIR, f"temp_{interaction.id}.jpg")
        await attachment.save(img_path)

        try:
            now = datetime.datetime.now()
            sheet_name = f"{now.year} {now.month}月"
            sh = self.workbook.worksheet(sheet_name)

            with open(img_path, "rb") as f:
                img_data = f.read()

            prompt = f"""
            Extract receipt data as a JSON LIST. 
            ### 1. Payment Mapping (CRITICAL)
            - IF the receipt mentions "Rakuten Pay", "R-Pay", or "楽天ペイ" -> SET payment to "Credit Rakuten JCB".
            - Otherwise, use the best match from: {self.payment_methods}

            ### 2. Expense Type Logic
            Categorize every item into one of these type: {self.expense_type}

            ### 3. Category Mapping
            - Use the most accurate value from: {self.categories}

            ### Output Requirements:
            - Format: [{{ "date": "YYYY-MM-DD", "amount_jpy": num, "items": "str", "category": "str", "store": "str", "payment": "str", "type": "str", "details": "summary" }}]
            """

            response = self.ai_client.models.generate_content(
                model=self.latest_model,
                contents=[
                    types.Part.from_text(text=prompt),
                    types.Part.from_bytes(data=img_data, mime_type="image/jpeg")
                ]
            )

            receipt_list = json.loads(response.text.replace('```json', '').replace('```', '').strip())
            if isinstance(receipt_list, dict): receipt_list = [receipt_list]

            # Logic preserved exactly as requested
            col_c = sh.col_values(3)
            target_index = 3
            for i in range(2, len(col_c)):
                if not col_c[i].strip():
                    target_index = i + 1; break
                target_index = i + 2
            
            last_row = target_index - 1
            f_b = ""
            f_d = ""

            for data in receipt_list:
                new_row = [data['date'], f_b, data['amount_jpy'], f_d, data['items'], 
                        data['category'], data['store'], data['payment'], data.get('type', 'Want'), data['details']]
                sh.insert_row(new_row, index=target_index, value_input_option='USER_ENTERED')
                target_index += 1

            await status_msg.edit(content=f"✅ Logged {len(receipt_list)} items to **{sheet_name}** after row {last_row} using {self.latest_model}.")
            #await status_msg.delete(delay=10.0)

        except Exception as e:
            await status_msg.edit(content=f"❌ Error: {str(e)}")
        finally:
            if os.path.exists(img_path): os.remove(img_path)
    
async def setup(bot):
    await bot.add_cog(ExpenseTracker(bot))