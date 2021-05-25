from os import rename
from re import I
from typing import Callable, Optional
import discord
from discord.embeds import Embed
from discord.ext import commands
import datetime as dt
from ..bot import CDBot
from .. import config


class Moderation(commands.Cog):
    """Commands for server moderation"""
    
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    @commands.command()
    async def kick(self, ctx: commands.Context, member: discord.Member, *, reason: Optional[str] = None):
        """Kick a member from the server"""
        if not ctx.author.top_role > member.top_role and ctx.author.id != ctx.guild.owner_id:
            raise commands.CheckFailure("You are not high enough in role hierarchy to kick that user")

        try:
            await member.send(f"You were kicked from {ctx.guild}\n**Reason:** {reason}")
        except discord.Forbidden:
            pass  # ignored
        except discord.HTTPException:
            pass  # ignored

        embed = discord.Embed(
            description=f"{member} was kicked by {ctx.author}\n**Reason:** {reason}",
                         colour=config.COLOUR_INFO)
        await member.kick(reason=reason)
        await ctx.send(embed=embed)

    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    @commands.group(invoke_without_command=True)
    async def ban(self, ctx: commands.Context, member: discord.Member, *, reason: Optional[str] = None):
        """Ban a member form the server.

        Note: This command deletes one day worth of the target's messages. Use `ban keep` keep the messages"""
        await self._ban_impl(ctx, member, reason, False)

    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    @ban.command(name="keep", aliases=["save"])
    async def ban_keep(self, ctx: commands.Context, member: discord.Member, *, reason: Optional[str] = None):
        """Bans a member from the server, does not delete thier messages"""
        await self._ban_impl(ctx, member, reason, True)

    async def _ban_impl(self, ctx: commands.Context, member: discord.Member, reason: Optional[str], keep: bool):
        if not ctx.author.top_role > member.top_role and ctx.author.id != ctx.guild.owner_id:
            raise commands.CheckFailure("You are not high enough in role hierarchy to ban that user")

        try:
            await member.send(f"You were banned from {ctx.guild}\n**Reason:** {reason}")
        except discord.Forbidden:
            pass  # ignored
        except discord.HTTPException:
            pass  # ignored

        await member.ban(reason=reason, delete_message_days = 0 if keep else 1)

        embed = discord.Embed(
            description=f"{member} was banned by {ctx.author}\n**Reason:** {reason}",
                         colour=config.COLOUR_INFO)
        await ctx.send(embed=embed)

    async def _purge_impl(self, ctx: commands.Context, search: int,
                          check: Callable[[discord.Message], bool]) -> None:
        if search > 1000:
            raise commands.UserInputError("Can't purge more than 1000 messages at a time.")

        past_14_days = dt.datetime.now() - dt.timedelta(days=14)
        deleted_count = 0

        # Bulk delete in chunks of 100
        while search > 0:
            limit = min(100, search)

            to_delete = []
            async for message in ctx.history(limit=limit,
                                             after=past_14_days, oldest_first=False):
                if message == ctx.message:
                    continue
                if check(message):
                    to_delete.append(message)

            await ctx.channel.delete_messages(to_delete)

            search -= limit
            deleted_count += len(to_delete)

        await ctx.message.delete()

        if deleted_count > 0:
            await ctx.send(
                embed=Embed(
                    description=f"Sucessfully purged {deleted_count} messages",
                    colour=config.COLOUR_INFO
                ),
                delete_after=5
            )
        else:
            await ctx.send(
                embed=Embed(
                    description="No messages were deleted, make sure messages are not older than 14 days",
                    colour=config.COLOUR_ERROR
                ),
                delete_after=5
            )

    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    @commands.group(invoke_without_command=True)
    async def purge(self, ctx: commands.Context, search: int = 100):
        """Deletes messages, optionally supports filters for which messages to delete.
        See `help purge` for more info on filter sub-commands."""
        await self._purge_impl(ctx, search, lambda _: True)

    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)    
    @purge.command(name="user")
    async def purge_user(self, ctx: commands.Context, search: Optional[int], user: discord.Member):
        """Purge messages only from a specific user"""
        if search is None:
            search = 100
        await self._purge_impl(ctx, search, lambda message: message.author == user)

    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    @purge.command(name="contains")
    async def purge_contains(self, ctx: commands.Context, search: Optional[int] = 100, *, contains: str):
        """Purge messages containing a sub-string"""
        await self._purge_impl(ctx, search, lambda message: contains in message.content)

    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    @purge.command(name="bot")
    async def purge_bot(self, ctx: commands.Context, search: Optional[int] = 100, *, prefix: Optional[str] = None):
        """Purge messages sent by bots, optionally with a prefix"""
        def check(message: discord.Message):
            return message.author.bot or \
                prefix is not None and message.content.startswith(prefix)
        await self._purge_impl(ctx, search, check)

    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    @purge.command(name="human")
    async def purge_human(self, ctx: commands.Context, search: Optional[int] = 100):
        """Purge non-bot messages"""
        await self._purge_impl(ctx, search, lambda message: not message.author.bot)

    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    @purge.command(name="files")
    async def purge_files(self, ctx: commands.Context, search: Optional[int] = 100):
        """Purges all messages with file attachments"""
        await self._purge_impl(ctx, search, lambda message: bool(message.attachments))

    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    @purge.command(name="embeds")
    async def purge_embeds(self, ctx: commands.Context, search: Optional[int] = 100):
        """Purge all messages with embeds"""
        await self._purge_impl(ctx, search, lambda message: bool(message.embeds))


def setup(bot: CDBot):
    bot.add_cog(Moderation())
