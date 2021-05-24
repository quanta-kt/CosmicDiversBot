import discord
from discord.ext import commands
import io
import traceback
from ..bot import CDBot
from .. import config


class ErrorHandler(commands.Cog):
    """Handles exceptions thrown during command invocations"""

    def __init__(self, bot: CDBot) -> None:
        super().__init__()
        self.bot = bot
        self._crash_log_webhook = None

    async def get_crash_log_webhook(self) -> discord.Webhook:
        return self._crash_log_webhook if self._crash_log_webhook is not None \
            else await self.bot.fetch_webhook(config.CRASH_WEBHOOK_ID)

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError) -> None:
        if isinstance(error, commands.CommandNotFound):
            return  # Ignored

        # User-friendly errors dispatched as messages
        if isinstance(error, commands.CheckFailure):
            await ctx.send(embed=discord.Embed(color=config.COLOUR_ERROR,
                description=str(error)))
            return
        if isinstance(error, commands.UserInputError):
            await ctx.send(embed=discord.Embed(colour=config.COLOUR_ERROR,
                title="Invalid arguments", description=str(error)))
            return
        
        # Report unexpected
        await self.unexpected_command_error(ctx, error)

    async def unexpected_command_error(self, ctx: commands.Context, error: commands.CommandError) -> None:
        await ctx.send("An unexpected error ocurred while processing your command.\n"
                       "This is most likely a bug in my code.",
                       reference=ctx.message)
        content = (f"Unexpected exception in command `{ctx.command.qualified_name}`\n"
                   f"User: {ctx.channel.id}\n"
                   f"Guild: {ctx.guild.id}\n"
                   f"Channel: {ctx.channel.id}\n"
                   f"Message URL: {ctx.message.jump_url}")

        tb = "".join(traceback.format_tb(error.__traceback__))
        originial = error.__cause__
        if originial is not None:
            tb += "\nOriginal exception:\n"
            tb += "".join(traceback.format_tb(originial.__traceback__))

        tb += f"\n{error}"
        await self.report_crash(content, tb)

    async def report_crash(self, message: str, tb):
        """Logs crash through a webhook message"""
        destination = await self.get_crash_log_webhook()
        await destination.send(message,
            file=discord.File(io.StringIO(tb), "crash.txt"))
    

def setup(bot: CDBot) -> None:
    bot.add_cog(ErrorHandler(bot))
