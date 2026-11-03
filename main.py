import os
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Configuration
basedir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(basedir, '.env'))

TOKEN = os.getenv('TOKEN')

if TOKEN is None:
    print(f"❌ ERROR: Token not found in: {os.path.join(basedir, '.env')}")
else:
    print(f"✅ Token loaded successfully.")

default_prefixes = ["get ", "c.", "c. ", "C.", "C. "]

intents = discord.Intents.all()
bot = commands.Bot(
    command_prefix=default_prefixes,
    intents=intents,
    case_insensitive=True
)

@bot.event
async def on_ready():
    # 1. Set Presence
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="get"))
    
    # 2. Sync Slash Commands
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} slash commands")
    except Exception as e:
        print(f"❌ Error syncing commands: {e}")
    
    print(f"🚀 Bot is ready: {bot.user.name}")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CommandNotFound):
        print(f"❓ Command not found: {ctx.message.content}")
        return
    print(f"❌ Error: {error}")

async def load_extensions():
    cogs_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cogs')
    for filename in os.listdir(cogs_path):
        if filename.endswith('.py'):
            try:
                await bot.load_extension(f'cogs.{filename[:-3]}')
                print(f"📦 Loaded extension: {filename}")
            except Exception as e:
                print(f"❌ Failed to load {filename}: {e}")

async def main():
    async with bot:
        await load_extensions()
        await bot.start(TOKEN)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass