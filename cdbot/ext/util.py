import discord
from discord.ext import commands, menus
from typing import Union
from ..bot import CDBot
from .. import config
from ..services import ElementNotFoundError, PeriodicTable, WikipediaApi


class WikipediaSearchResultsSource(menus.AsyncIteratorPageSource):
    """Page source for Wikipedia search results, lazily fetches the page extract"""
    def __init__(self, query, api: WikipediaApi):
        super().__init__(self, per_page=1)
        self.api = api
        self.query = query

        # async iteration state
        self.page_count = None
        self._aiter_current = 0
        self._search_results = None

    def __aiter__(self):
        return self
    
    async def __anext__(self):
        if self._search_results is not None and self._aiter_current >= self.page_count:
            raise StopAsyncIteration

        # Fetch search results if they don't exist
        if not self._search_results:
            self._search_results = (await self.api.search(self.query))["pages"]
            self.page_count = len(self._search_results)

        current = self._search_results[self._aiter_current]

        # Fetch extract for current search result
        extract = await self.api.page_extract(current["id"])

        if thumbnail := current.get("thumbnail"):  # nullable
            thumbnail_url = "https:" + thumbnail["url"]
        else:
            thumbnail_url = None

        # Track iteration
        self._aiter_current += 1

        return {
            "title": current["title"],
            "description": extract or current.get("description") or "*[Summary unavailable]*",
            "url": WikipediaApi.ARTICLE_URL_F % current["key"],
            "colour": config.COLOUR_INFO,
            "thumbnail_url": thumbnail_url
        }

    async def format_page(self, menu, page):
        embed = discord.Embed(**page)
        embed.set_footer(text=f"Page {menu.current_page + 1} of {self.page_count}")
        if page["thumbnail_url"]:  # nullable
            embed.set_thumbnail(url=page["thumbnail_url"])
        return embed

class Util(commands.Cog):
    """Utility commands"""
    def __init__(self, bot: CDBot) -> None:
        super().__init__()
        self.wikipedia_api = WikipediaApi(bot.http_client)
        self.periodic_table = PeriodicTable()

    @commands.command()
    async def wiki(self, ctx: commands.Context, *, query: str):
        """Fetch articles from Wikipedia.org"""
        source = WikipediaSearchResultsSource(query, self.wikipedia_api)
        await menus.MenuPages(source).start(ctx)

    @commands.command()
    async def element(self, ctx: commands.Context, search: Union[int, str]) -> None:
        """Get info of an element on the periodic table. Search by name or the atomic number"""
        if isinstance(search, str):
            element = self.periodic_table.get_element_by_name(search)
        else:
            element = self.periodic_table.get_element_by_atomic_number(search)
        
        await ctx.send(embed=PeriodicTable.embed(element))
    
    @element.error
    async def element_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, ElementNotFoundError):
            await ctx.send(embed=discord.Embed(description=str(error), colour=config.COLOUR_ERROR))
        else:
            raise error


def setup(bot: CDBot):
    bot.add_cog(Util(bot))
