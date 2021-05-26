import discord
from discord.ext import commands
from discord.ext.commands.core import Command
from ..bot import CDBot
from .. import config


class EmbedPaginator(commands.Paginator):

    def __init__(self):
        super().__init__(prefix=None, suffix=None)
        self.title = None

    @property
    def pages(self) -> list[discord.Embed]:
        return [
            discord.Embed(title=self.title, description=page + f"\n\n", colour=config.COLOUR_INFO) \
                .set_thumbnail(url=config.THUMBNAIL_URL)
            for page in super().pages
        ]

class CustomHelp(commands.MinimalHelpCommand):

    def __init__(self):
        super().__init__(no_category="Help",
            paginator=EmbedPaginator()
        )

    def get_opening_note(self):
        None

    def get_ending_note(self):
        return (f"Use `{self.clean_prefix}{self.invoked_with} [command]` for more info on a command.\n"
               + f"You can also use `{self.clean_prefix}{self.invoked_with} [category]` for more info on a category."
               + f"\n\nMade with <3 by **{config.CREATOR_NAME}**""")

    def get_command_signature(self, command):
        return f"{self.clean_prefix}{command.qualified_name} {command.signature}".strip()

    def add_command_formatting(self, command: commands.Command):
        if command.description:
            self.paginator.add_line(command.description, empty=True)

        self.paginator.add_line(f"**Syntax:** `{self.get_command_signature(command)}`")

        if command.help:
            try:
                self.paginator.add_line(command.help, empty=True)
            except RuntimeError:
                for line in command.help.splitlines():
                    self.paginator.add_line(line)
                self.paginator.add_line()
        
        if command.aliases:
            self.paginator.add_line(f"**Aliases:** {', '.join(f'`{alias}`' for alias in command.aliases)}")

    def add_subcommand_formatting(self, command):
        self.paginator.add_line(f"`{command.qualified_name}` {command.short_doc}")

    def add_bot_commands_formatting(self, commands, heading):
        if commands:
            self.paginator.add_line(f"**{heading}**")
            self.paginator.add_line(", ".join(f"`{cmd}`" for cmd in commands), empty=True)

    async def send_pages(self):
        destination = self.get_destination()
        for page in self.paginator.pages:
            await destination.send(embed=page)

    async def send_bot_help(self, mapping):
        self.paginator.title = "Cosmic Divers Bot"
        await super().send_bot_help(mapping)

    async def send_cog_help(self, cog):
        self.paginator.title = f"Commands category: {cog.qualified_name}"
        await super().send_cog_help(cog)

    async def send_command_help(self, command):
        self.paginator.title = f"Help on command {command.qualified_name}"
        await super().send_command_help(command)

    async def send_group_help(self, group):
        self.paginator.title = f"Command group {group.qualified_name}"
        await super().send_group_help(group)


def setup(bot: CDBot):
    bot.help_command = CustomHelp()
