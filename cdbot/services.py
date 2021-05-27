import aiohttp
from discord import utils
import discord
from discord.ext import commands
import json
from typing import Dict


class WikipediaApi:
    TITLE_SEARCH_URL = "https://api.wikimedia.org/core/v1/wikipedia/en/search/title"
    MEDIA_WIKI_API_URL = "https://en.wikipedia.org/w/api.php"
    ARTICLE_URL_F = "https://en.wikipedia.org/wiki/%s"

    def __init__(self, http_client: aiohttp.ClientSession) -> None:
        self.http = http_client

    async def search(self, query: str) -> Dict:
        params = {
            "q": query,
            "limit": 10
        }
        async with self.http.get(self.TITLE_SEARCH_URL, params=params) as resp:
            return await resp.json()

    async def page_extract(self, page_id) -> str:
        params = {
	        "action": "query",
	        "format": "json",
	        "prop": "extracts",
            "exchars": 1000,
           	"explaintext": 1,
            "exsectionformat": "plain",
            "pageids": page_id,
        }
        async with self.http.get(self.MEDIA_WIKI_API_URL, params=params) as resp:
            data = await resp.json()
        return data["query"]["pages"][str(page_id)]["extract"]

class ElementNotFoundError(commands.CommandError):
    pass

class PeriodicTable:

    def __init__(self) -> None:
        with open("data/periodic_table.json") as fp:
            self.data: list = json.load(fp)["elements"]

    def get_element_by_atomic_number(self, atomic_number: int) -> dict:
        if atomic_number < 0 or atomic_number > len(self.data):
            raise ElementNotFoundError(f"{atomic_number} is not a valid atomic number of an atom.")
        return self.data[atomic_number - 1]
    
    def get_element_by_name(self, element_name: str) -> dict:
        element_name = element_name.title()
        element = utils.find(lambda x: x["name"] == element_name, self.data)

        if not element:
            raise ElementNotFoundError(f"Element {element_name} not found.")
        return element

    @staticmethod
    def embed(element: dict) -> discord.Embed:
        element = element.copy()  # make sure we don't make changes to the passed dictionary

        embed = discord.Embed(title=element.pop("name"), colour=int(element.pop("cpk-hex"), base=16))        
        embed.url = element.pop("source")

        embed.add_field(name="Boiling point", value=str(element.pop("boil")) + ' K')
        embed.add_field(name="Melting point", value=str(element.pop("melt")) + ' K')

        element.pop("spectral_img")  # unused

        for key, value in element.items():
            # Transform lists to comma separated values
            if isinstance(value, list):
                value = ", ".join(str(x) for x in value)
            embed.add_field(name=" ".join(key.split("_")).title(), value=value)

        return embed
