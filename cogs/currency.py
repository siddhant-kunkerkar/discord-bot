import discord, asyncio, datetime, json, random, os, math
from discord.ext import commands
from discord.ext.commands import BucketType
from discord import Embed, Guild 


#global variables
currency_unit = 'dimes'
cogs_path = os.path.dirname(os.path.abspath(__file__))

class Currency(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def get_currency_data(self):
        """Returns json file data as a json object"""
        with open (os.path.join(cogs_path,u"user_credits.json"), "r") as uc:
            users = json.load (uc)
            return users
            uc.close ()

    async def write_currency_data(self, user :json):
        with open (os.path.join(cogs_path,"user_credits.json"), "w") as uc:
            json.dump (user, uc)
            uc.close ()

    async def check_if_new(self, user: discord.Member):
        """checks if the user already exists in db or not
        Returns true if user exists in db else returns false"""

        users_list = await self.get_currency_data ()

        if str(user.id) not in users_list:
            print("new user joined")
            users_list [str (user.id)] = {}
            users_list [str (user.id)] ["wallet"] = 420
            users_list [str (user.id)] ["bank"] = 420
            await self.write_currency_data (users_list)
            return True
        else:
            return False

    @commands.command(name = "grind", aliases = ["search"], description = "Grinds random number of coins in between 0 to 50")
    @commands.cooldown(1, 20, type = BucketType.user )
    async def grind(self, ctx):
        user = ctx.author 
        await self.check_if_new(user)
        users_list = await self.get_currency_data()
        bag = users_list [str (user.id)] ["wallet"]
        res = random.choice(list(range(0, 50)))
        bag += res
        users_list [str (user.id)] ["wallet"] = bag
        await self.write_currency_data(users_list)

        emb = discord.Embed(title = 'Money Play', color = discord.Color.green(), description = "Grinding ..." )
        embd = discord.Embed(title = 'Money Play', color = discord.Color.green(), description = f"You got {res} {currency_unit} ")

        msg = await ctx.send(embed = emb)
        await asyncio.sleep(1)
        await msg.edit(content = None , embed = embd) 
    
    @grind.error
    async def grind_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = 'You need to wait for {:.3f}s before using this command again'.format(error.retry_after)
            await ctx.send(msg)
        else:
            raise error

    @commands.command (name = "beg", description = "This is a fun command referenced to Dank Memer Bot")
    @commands.cooldown(1, 5, type = BucketType.user)
    async def beg(self, ctx):
        """This is a fun command referenced to Dank Memer Bot"""

        beg_embed = discord.Embed (title = f"No begging, move ahead :slight_smile:",
                                   description = f"**If you want to beg go beg on <:pepesad:799620797722656779>** \n "
                                                 "We do not want our users to beg ",
                                   color = discord.Color.red ())
        beg_embed.set_footer (text = f"Psst...You can grind coins with grind cmd")
        await ctx.send (embed = beg_embed)
    @beg.error
    async def beg_error(skef, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = 'You need to wait for {:.3f}s before using this command again'.format(error.retry_after)
            await ctx.send(msg)
        else:
            raise error

    @commands.command (name = 'gamble', aliases = ['diceroll', 'bet','roll'], description = f"Gamble some {currency_unit}", usage = f"`go gamble <amt>`")
    async def roll(self, ctx, * , user_bet = ""):
        pc = random.choice (range (1, 13))
        user_threw = random.choice (range (1, 13))
        user = ctx.author
        win_percent = float (random.choice (range (30, 400)))
        users_list = await self.get_currency_data ()
        bag = users_list [str (user.id)] ["wallet"]
        acceptable = ["max", "all", range(1, int(bag))]
        botname = self.bot.user.name 
        player = user.name

        if user_bet in acceptable or user_bet != "":
            if user_bet == "max" or user_bet == "all":
                user_bet = 100000
            else:
                user_bet = int (user_bet)
            if user_bet > bag:
                await ctx.send (
                    f"I am a bot, not a fool. You do not have that many {currency_unit}. "
                    f"Go get more {currency_unit} "
                )
            elif user_bet < 500:
                await ctx.send (
                    f"Sorry, You must bet atleast a 500 {currency_unit}"
                )
            elif user_bet > 100000:
                await ctx.send(f"Sorry, you can bet only 100000 {currency_unit} at a time")
            elif user_bet <= bag :
                rolling = discord.Embed(title = "Casino", description = "**Rolling...**", color = discord.Color.green())
                msg = await ctx.send(embed = rolling)
                await asyncio.sleep(2)
                if pc < user_threw:
                    winnings = int (user_bet * win_percent / 100)
                    bag += winnings
                    win_embed = discord.Embed (
                        title = "Casino",
                        color = discord.Color.green (),
                        description =
                        f' Hurray ! You Won {winnings} {currency_unit} \n '
                        f'You now have {bag} {currency_unit} \n'
                        f'You threw : {user_threw} \n'
                        f'{botname} threw : {pc}')
                    win_embed.set_footer(text = "If you feel bot is slow, then note that embeds have a delay of 2s for that effect")
                    users_list [str (user.id)] ["wallet"] = bag
                    await self.write_currency_data(users_list)
                    await msg.edit (embed = win_embed)
                elif pc > user_threw:
                    bag = int (bag - user_bet)
                    lose_embed = discord.Embed (
                        title = "Casino",
                        color = discord.Color.red (),
                        description = f' Oops, you lost {user_bet} {currency_unit} \n'
                                      f' You now have {bag} {currency_unit} \n You threw : {user_threw} \n'
                                      f' {botname}  threw : {pc}')
                    lose_embed.set_footer(text = "If you feel bot is slow, then note that embeds have a delay of 2s for that effect")                 
                    users_list [str (user.id)] ["wallet"] = bag                 
                    await self.write_currency_data(users_list)
                    await msg.edit (embed = lose_embed)
                elif pc == user_threw:
                    tie_embed = discord.Embed (
                        title = "Casino",
                        color = discord.Color.blue (),
                        description =
                        f' Its a tie, you didn\'t lose anything \nYou threw : {user_threw} \n'
                        f'{botname}  threw : {pc}')
                    tie_embed.set_footer(text = "If you feel bot is slow, then note that embeds have a delay of 2s for that effect")      
                    await msg.edit (embed = tie_embed)
            else:
                await ctx.send (
                    f"You can only gamble {currency_unit} here ! :expressionless:")
        else:
            await ctx.send (f'You need to bet something !! smh :face_palm:')

    """Following section contains Currency commands from scratch """

    @commands.command (aliases = ['cred'],  description = "Check your or someone's balance", usage = "`get bal` [user]")
    async def bal(self, ctx, user: discord.Member = ""):

        """Shows your or mentioned user's current balance"""
        new_user_embed = discord.Embed (title = f"Welcome to World of Money Play {ctx.author.name}",
            description =f"Use `do help` for a list of commands \n Try out all the commands and have fun !!",
            color = discord.Color.blue ())

        users_list = await self.get_currency_data()

        if await self.check_if_new(ctx.author) :
            await ctx.send (embed = new_user_embed)
            user_id = ctx.author.id
            user_name = ctx.author.name
        elif user != "":
            if isinstance (user, int):
                user_id = user
                user_obj = await Guild.fetch_member (self.bot, member_id = user_id)
                user_name = user_obj.name
            elif isinstance(user, discord.Member):
                user_id = user.id
                user_name = user.name
            else:
                await ctx.send("Either the user does not exist or they do not use the bot")
        else:
            user_id = ctx.author.id
            user_name = ctx.author.name

        bag_bal = users_list [str (user_id)] ["wallet"]
        bank_bal = users_list [str (user_id)] ["bank"]

        balance_embed = discord.Embed (title = f"{user_name}'s balance ", color = discord.Color.green ())
        balance_embed.add_field (name = 'Bag : ', value = f"{bag_bal} {currency_unit}")
        balance_embed.add_field (name = "Bank : ", value = f"{bank_bal} {currency_unit}", inline = False)

        emb_1 = discord.Embed(title = f"{user_name}'s balance ", color = discord.Color.green (), description = "**Checking Balance...**" )

        msg = await ctx.send(embed = emb_1)
        await asyncio.sleep(1)
        await msg.edit(content = None, embed = balance_embed)

    @commands.command(name = "pay", aliases = ["share", "give"], description = "Share currency with a user", usage = "`go pay <user> <amt>")

    async def pay(self, ctx, user:discord.Member = None, amt: int = 0):

        #global sender_bag, receiver_bag, receiver_id, sender_id, users_list, bag
        users_list = await self.get_currency_data ()
        sender = ctx.author
        sender_id = sender.id
        try:
            if isinstance(user, discord.Member):
                receiver = user
                receiver_id = receiver.id
        except:
            await ctx.send("You did not use this command properly\n"
                        "The correct usage is do pay `<user> <amount>`")
        try:
            sender_bag = users_list [str (sender_id)] ["bank"]
            receiver_bag = users_list [str (receiver_id)] ["bank"]
        except:
            await ctx.send ("Looks like the user you are paying does not exist or they do not use the bot")

        if amt in ["",None] or amt < 1 or amt > sender_bag:

            fail_msg = f"**Transaction Failed, Invalid Amount** \n"
            f"You cannot pay {amt} {currency_unit}. Check your input and try again"

            await ctx.send(fail_msg)
        elif amt in range(0, sender_bag):

            sender_bag -= amt
            receiver_bag = +amt
            users_list [str (sender_id)] ["bank"] = sender_bag
            users_list [str (receiver_id)] ["bank"] = receiver_bag

            pay_in_prog = discord.Embed(title = "Wire transfer in progress...", color = discord.Color.green())
           
            paid_msg = discord.Embed(title = "Wire Transfer Complete", description = f"{sender.mention} , You paid {receiver.mention} {amt} {currency_unit}. \n"
                        f"Now you have {sender_bag} {currency_unit} ", color = discord.Color.green())
            
            await self.check_if_new(receiver)
            await self.write_currency_data(users_list)
            msg = await ctx.send(embed = pay_in_prog)
            await asyncio.sleep(2)
            await msg.edit(content = None, embed = paid_msg)

# CRITICAL FIX: This must be async for modern discord.py
async def setup(bot):
    await bot.add_cog(Currency(bot))
