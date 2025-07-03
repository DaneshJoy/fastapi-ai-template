import requests
import trafilatura
# from tavily import TavilyClient
from duckduckgo_search import DDGS
from duckduckgo_search.exceptions import (
    ConversationLimitException,
    RatelimitException,
    TimeoutException,
)

from config import Settings


settings = Settings()
# tavily_client = TavilyClient(api_key=settings.TAVILY_API_KEY)


class SearchService:
    def web_search(self, query: str):
        try:
            results = []

            # Serper Search
            # response = requests.post(
            #     "https://google.serper.dev/search",
            #     headers={"X-API-KEY": settings.SERPER_API_KEY},
            #     json={"q": query}
            # )
            # search_results = response.json().get('organic', [])

            # Tavily Search (content included)
            # response = tavily_client.search(
            #     query=query,
            #     max_results=5,
            #     include_raw_content=True,  # Get full content from Tavily
            #     include_answer=False       # We just want search results, not AI answer
            # )
            # search_results = response.get('results', [])

            # Duckduckgo Search
            try:
                search_results = DDGS().text(query, max_results=5)
            except ConversationLimitException:
                print("ConversationLimitException")
                return None
            except RatelimitException:
                print("RatelimitException")
                return None
            except TimeoutException:
                print("TimeoutException")
                return None

            # Brave Search
            # search_results = requests.get(
            #     "https://api.search.brave.com/res/v1/web/search",
            #     headers={
            #         "Accept": "application/json",
            #         "Accept-Encoding": "gzip",
            #         "x-subscription-token": "BSAEx9eYIrhXgLFzIS8bHrdvQHXA6Gw"
            #     },
            #     params={
            #         "q": query,
            #         "count": "5",
            #         "text_decorations": "false",
            #         "summary": "true"
            #     },
            #     timeout=10
            # ).json()
            # search_results = search_results['web']['results']

            for result in search_results:
                config = trafilatura.settings.use_config()
                config.set("DEFAULT", "DOWNLOAD_TIMEOUT", "5")
                config.set("DEFAULT", "USER_AGENTS",
                           "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:41.0) Gecko/20100101 Firefox/41.0")
                download = trafilatura.fetch_url(result.get('href', '') or result.get('url', ''),
                                                 no_ssl=True,
                                                 config=config)
                content = trafilatura.extract(download, include_comments=False)

                results.append({
                    "title": result.get('title', ''),
                    "url": result.get('href', '') or result.get('url', ''),
                    "content": content,
                    # "content": result.get('body', '') or result.get('content', '') or result.get('description', ''),
                })

            return results
        except Exception as e:
            print(e)
