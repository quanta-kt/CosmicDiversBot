import discord
from discord import embeds
from discord import colour
from discord.ext import commands
from discord.ext.commands.core import command, has_permissions
from discord.permissions import Permissions
from ..bot import CDBot
from .. import config


class Config(commands.Cog):
    """Bot configuration/settings"""

    def __init__(self, bot: CDBot) -> None:
        super().__init__()
        self.bot = bot
    
    @has_permissions(manage_guild=True)
    @commands.command()
    async def prefix(self, ctx: commands.Context, *, prefix: str):
        """Update bot's prefix for this guild"""

        if len(prefix) > 6:
            embed = discord.Embed(
                description=f"Prefix length can't exceed 6 characters.",
                colour=config.COLOUR_ERROR
            )
            await ctx.send(embed)
            return

        doc = self.bot.db.prefixes
        await doc.replace_one({"_id": ctx.guild.id}, {"prefix": prefix}, upsert=True)
        # Update cached prefix
        self.bot.guild_prefixes[ctx.guild.id] = prefix

        embed = discord.Embed(description=f"Prefix is now set to: {prefix}",
                              colour=config.COLOUR_INFO)
        await ctx.send(embed=embed)
    

def setup(bot: CDBot):
    bot.add_cog(Config(bot))
