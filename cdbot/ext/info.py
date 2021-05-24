import discord
from discord import embeds
from discord.ext import commands
from discord.ext.commands.core import command
from ..bot import CDBot
from .. import config


class Info(commands.Cog):
    
    @commands.command()
    async def source(self, ctx: commands.Context):
        """Get a link to view my source code!"""
        embed = discord.Embed(
            description=f"My source code is available [here]({config.GITHUB_URL})",
            colour=config.COLOUR_INFO) \
        .set_thumbnail(url="https://i.imgur.com/Bq0JdS3.png") \
        .set_footer(text="Feel free to open an issue or a PR")
        await ctx.send(embed=embed)
    

def setup(bot: CDBot):
    bot.add_cog(Info())
