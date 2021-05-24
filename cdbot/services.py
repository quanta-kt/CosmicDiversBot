import aiohttp
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
