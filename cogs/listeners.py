import discord
import asyncio
from discord.ext import commands
from discord.ext.commands import BucketType

# Global Variables from your original listeners
invite_link = "https://discord.com/api/oauth2/authorize?client_id=735912554873749565&permissions=8&scope=bot"
reddit_link = "https://www.reddit.com/r/DisBot_Lab/"
default_prefixes = ["get ", "c.", "c. ", "C.", "C. "]
trigs = {
    "anurag": 'Thandi !!', 
    "gholap": "Naav nako gheu tyacha bc", 
    "prince": '<a:potato_swag:761231936832143381>'
}

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        
        msg = message.content.lower()
        mentions = ['<@!735912554873749565>', '<@735912554873749565>']
        spl = msg.split()
        
        for i in spl:
            if i in mentions:
                await message.channel.send(f"Hey, my prefixes are: `{'; '.join(default_prefixes)}`")
            elif i in trigs:
                # Reaction logic from your file
                await message.channel.send(trigs[i])
                pass

    @commands.command(name="ping")
    async def ping(self, ctx):
        """Checks the bot's latency."""
        checking_ping_embed = discord.Embed(title='Checking Ping', color=discord.Color.blue())
        message = await ctx.send(embed=checking_ping_embed)

        latency = round(self.bot.latency * 1000)
        
        if self.bot.latency < 0.5:
            embed = discord.Embed(
                title='Pong! 🏓',
                description=f'Response Time: {latency} ms.\nWow! I\'m speed',
                color=discord.Color.green()
            )
        else:
            embed = discord.Embed(
                title='Pong! 🏓',
                description=f'Response Time: {latency} ms.\nOof! High Ping.',
                color=discord.Color.red()
            )
        
        embed.set_footer(text='DisBot Lab Team')
        await asyncio.sleep(0.5)
        await message.edit(embed=embed)

    @commands.command(name="invite", aliases=["inv"])
    async def invite(self, ctx):
        """Sends a link to invite bot to your server."""
        inv_embed = discord.Embed(
            title=f"Add {self.bot.user.name} to your server",
            description=f"[Invite Link]({invite_link})",
            color=discord.Color.dark_blue()
        )
        await ctx.send(embed=inv_embed)

    @commands.command(name="clear", aliases=['clr', 'purge'])
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int = 1):
        """Clears a specified amount of messages."""
        await ctx.channel.purge(limit=amount + 1)
        await ctx.send(f'{amount} messages deleted successfully.', delete_after=5)
    @commands.command(name="cleardm")
    async def cleardm(self, ctx, amount: int = 10):
        """Deletes the last X messages sent by the bot in this DM."""
        # Check if the message is actually in a DM
        if isinstance(ctx.channel, discord.DMChannel):
            # We iterate through the history of the DM
            async for message in ctx.channel.history(limit=amount):
                # The bot can only delete its own messages in DMs
                if message.author == self.bot.user:
                    try:
                        await message.delete()
                        # Small sleep to prevent Discord rate limits
                        await asyncio.sleep(0.5) 
                    except Exception as e:
                        print(f"Failed to delete message: {e}")
            
            # Send a temporary confirmation that also deletes itself
            await ctx.send("🧹 DM Cleanup complete.", delete_after=3)
        else:
            await ctx.send("❌ This command only works in our Private Messages.")

# CRITICAL FIX: This must be async for modern discord.py
async def setup(bot):
    await bot.add_cog(General(bot))