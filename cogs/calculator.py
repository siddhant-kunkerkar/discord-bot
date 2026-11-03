import discord, asyncio, datetime, random, os, json, math
from discord.ext import commands
from discord import Guild, Embed

#global variables

class calculator(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name = "rseries")
    async def rseries(self, ctx, type: str, lower: int, upper: int):
        i = 1
        temp = lower
        ty = int(type[1:])
        mult = pow(10, 1/ty)
        series = [str(lower)]
        while temp <= upper:
            temp = lower * pow(mult, i)
            i += 1
            print (str(temp))
            series.append(str(f"{temp:.3f}"))
        await ctx.send(f"The series is :{' ; '.join(series)}")

    

    @commands.command(name = "interpolate", 
    aliases = ["inpolate", "ip"], 
    description = "A command to interpolate a value between 2 points", 
    usage = "x1, y1, x2, y2, x (req pt.)")
    async def interpolate(self, ctx, a1: float, b1: float, a2: float, b2: float, x: float):
        calc = discord.Embed(title = "Calculating ...",
        color = discord.Color.orange(), description = "Please wait")

        msg = await ctx.send(embed = calc)

        try :
            num = a1 - x
            den = a1 - a2
            mult = b2 - b1
            interpolated = math.fabs((num/den)*mult) 

            result = discord.Embed(title = "Done ! :smile:",
        color = discord.Color.orange(), description = ("The interpolated value is  {:.3f}".format(interpolated)))
            
            await asyncio.sleep(2)
            await msg.edit(embed = result)
        except Exception as e:
            await ctx.send(f"There was an error with this command, {e} " )

async def setup(bot):
    await bot.add_cog(calculator(bot))