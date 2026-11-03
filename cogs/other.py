import discord, asyncio, datetime, random, os, json, math
from discord.ext import commands
from discord import Guild, Embed

#global variables

global options, reversed_options
options = {0: 'rock', 1: 'spock', 2: 'paper', 3: 'lizard', 4: 'scissor'}
reversed_options = dict (map (reversed, options.items ()))


class games(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # Rock paper scissor Lizard
    def name_to_num(self, name: str):
        try:
            return reversed_options[name]
        except KeyError:
            return False

    def num_to_name(self, num: int):
        try:
            return options[num]
        except KeyError:
            return False

    #Following function calculates result using above 2 function
    def play(self, user, comp):
        """Takes input string from user from the list
        return win if user wins, lose if user loses
        and tie if both throw same.
        """
        player_num = self.name_to_num(user)
        comp_num = self.name_to_num(comp)
        diff=int(comp_num - player_num)

        if diff in (1, 2, -3, -4):
            return "lose"
        elif diff == 0:
            return "tie"
        else:
            return "win"

    @commands.command (aliases = ['rspls', 'rpsls'])
    async def rps(self, ctx, user: str = ''):
        t_list = ['rock', 'spock', 'paper', 'lizard', 'scissor']
        o_list = ', '.join (t_list)
        bot_mention = self.bot.user.mention
        bot_name = self.bot.user.name
        user_mention = ctx.author.mention
        user_name = ctx.author.name
        if user == '':
            await ctx.send (f'You need to throw something from : {o_list}')
            return
        elif user in t_list:
            bot_throw = random.choice (t_list)
            user_throw = user
            result = self.play (user_throw, bot_throw)

            game_embed = discord.Embed (
                title = 'Rock Spock Paper Lizard Scissor',
                color = discord.Color.dark_blue ())

            message = await ctx.send (embed = game_embed)

            # Following embed will be shown when user wins
            win_embed = discord.Embed (
                title = 'You Won !!!',
                description =
                f'You threw: {user_throw} \n{bot_name}  threw : {bot_throw}',
                color = discord.Color.green ())

            # Following embed will be shown if user loses
            lose_embed = discord.Embed (
                title = 'You lost',
                description =
                f'You Threw : {user_throw} \n{bot_name}  threw : {bot_throw}',
                color = discord.Color.red ())

            # Following embed will be shown if user loses
            tie_embed = discord.Embed (
                title = 'Its a tie :| ',
                description =
                f'You threw : {user_throw} \n{bot_name}  threw : {bot_throw}',
                color = discord.Color.red ())
            await asyncio.sleep (2)
            # Conditional statements within elif for embeds edit
            if result == 'win':
                await message.edit (embed = win_embed)
            elif result == 'lose':
                await message.edit (embed = lose_embed)
            elif result == 'tie':
                await message.edit (embed = tie_embed)
        else:
            await ctx.send ("Thats not a valid choice noob. Type it properly and try again")

    @commands.command(name = "adduser", aliases = ["add"], description = "Adds a user to the bot db", hidden = True)
    @commands.is_owner()
    async def add_user(self, ctx, user: discord.Member = ""):
        """Add a user to the currency system"""
        if user == "":
            await ctx.send("Dad, how are we gonna add nobody, smh")

        else:
            with open ("/home/runner/CleverZestyPlans/cogs/user_credits.json", "r") as uc:
                users_list = json.load (uc)
            uc.close ()
            users_list [str (user.id)] = {}
            users_list [str (user.id)] ["wallet"] = 420
            users_list [str (user.id)] ["bank"] = 420
            with open ("/home/runner/CleverZestyPlans/cogs/user_credits.json", "w") as uc:
                json.dump (users_list, uc)
            uc.close ()
            await ctx.send(f"Added {user.name} :white_check_mark:")


# CRITICAL FIX: This must be async for modern discord.py
async def setup(bot):
    await bot.add_cog(games(bot))