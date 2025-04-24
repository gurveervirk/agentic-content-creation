from llama_index.readers.web import NewsArticleReader
from newsapi import NewsApiClient
import os
from typing import List, Dict, Any, Optional

class News:
    """A wrapper class for interacting with the NewsAPI and reading article content."""
    def __init__(self):
        """Initializes the NewsApiClient and NewsArticleReader."""
        self.newsapi_client = NewsApiClient(api_key=os.getenv("NEWS_API_KEY"))
        self.reader = NewsArticleReader()

    def read_news_articles(self, urls: List[str]) -> List[str]:
        """Reads the main content of news articles from a list of URLs.

        Uses the initialized NewsArticleReader to fetch and parse articles.
        Filters out articles where the text content could not be extracted.

        Args:
            urls (List[str]): A list of URLs pointing to news articles.

        Returns:
            List[str]: A list of strings, where each string is the extracted text content
                       of a successfully parsed article.
        """
        articles = self.reader.load_data(urls)
        articles = [article.text for article in articles if article.text] # Simplified list comprehension
        return articles

    def get_top_headlines( 
        self,
        q: Optional[str],
        sources: Optional[str],
        category: Optional[str],
        language: Optional[str],
        country: Optional[str],
        page_size: Optional[int],
        page: Optional[int],
    ) -> Dict[str, Any]:
        """Fetches top headlines from the NewsAPI.

        Calls the underlying `newsapi_client.get_top_headlines` method.
        Refer to the NewsAPI documentation for detailed parameter descriptions:
        https://newsapi.org/docs/endpoints/top-headlines

        Args:
            q (Optional[str]): Keywords or phrases to search for in the article title and body.
            sources (Optional[str]): A comma-separated string of identifiers for the news sources or blogs you want headlines from.
            category (Optional[str]): The category you want to get headlines for (e.g., business, entertainment, health).
            language (Optional[str]): The 2-letter ISO-639-1 code of the language you want to get headlines for.
            country (Optional[str]): The 2-letter ISO 3166-1 code of the country you want to get headlines for.
            page_size (Optional[int]): The number of results to return per page (default is 20, max is 100).
            page (Optional[int]): Use this to page through the results.

        Returns:
            Dict[str, Any]: The raw JSON response from the NewsAPI.
        """
        # Clean up the parameters to ensure int is int
        if page_size is not None:
            page_size = int(page_size)
        if page is not None:
            page = int(page)
        return self.newsapi_client.get_top_headlines(
            q=q,
            sources=sources,
            category=category,
            language=language,
            country=country,
            page_size=page_size,
            page=page,
        )

    def get_sources(
        self,
        category: Optional[str],
        language: Optional[str],
        country: Optional[str],
    ) -> Dict[str, Any]:
        """Fetches the available news sources from the NewsAPI.

        Calls the underlying `newsapi_client.get_sources` method.
        Use this to find identifiers for the `sources` parameter in other calls.
        Refer to the NewsAPI documentation for detailed parameter descriptions:
        https://newsapi.org/docs/endpoints/sources

        Args:
            category (Optional[str]): Find sources that display news of this category.
            language (Optional[str]): Find sources that display news in a specific language.
            country (Optional[str]): Find sources that display news in a specific country.

        Returns:
            Dict[str, Any]: The raw JSON response from the NewsAPI.
        """
        return self.newsapi_client.get_sources(
            category=category, language=language, country=country
        )

    def get_everything(
        self,
        q: Optional[str],
        qintitle: Optional[str],
        sources: Optional[str],
        domains: Optional[str],
        exclude_domains: Optional[str],
        from_param: Optional[str],
        to: Optional[str],
        language: Optional[str],
        sort_by: Optional[str],
        page_size: Optional[int],
        page: Optional[int],
    ) -> Dict[str, Any]:
        """Call the `/everything` endpoint.

        Search through millions of articles from over 30,000 large and small news sources and blogs.

        :param q: Keywords or a phrase to search for in the article title and body.  See the official News API
            `documentation <https://newsapi.org/docs/endpoints/everything>`_ for search syntax and examples.
        :type q: str or None

        :param qintitle: Keywords or a phrase to search for in the article title and body.  See the official News API
            `documentation <https://newsapi.org/docs/endpoints/everything>`_ for search syntax and examples.
        :type q: str or None

        :param sources: A comma-seperated string of identifiers for the news sources or blogs you want headlines from.
            Use :meth:`NewsApiClient.get_sources` to locate these programmatically, or look at the
            `sources index <https://newsapi.org/sources>`_.
        :type sources: str or None

        :param domains:  A comma-seperated string of domains (eg bbc.co.uk, techcrunch.com, engadget.com)
            to restrict the search to.
        :type domains: str or None

        :param exclude_domains:  A comma-seperated string of domains (eg bbc.co.uk, techcrunch.com, engadget.com)
            to remove from the results.
        :type exclude_domains: str or None

        :param from_param: A date and optional time for the oldest article allowed.
            If a str, the format must conform to ISO-8601 specifically as one of either
            ``%Y-%m-%d`` (e.g. *2019-09-07*) or ``%Y-%m-%dT%H:%M:%S`` (e.g. *2019-09-07T13:04:15*).
            An int or float is assumed to represent a Unix timestamp.  All datetime inputs are assumed to be UTC.
        :type from_param: str or datetime.datetime or datetime.date or int or float or None

        :param to: A date and optional time for the newest article allowed.
            If a str, the format must conform to ISO-8601 specifically as one of either
            ``%Y-%m-%d`` (e.g. *2019-09-07*) or ``%Y-%m-%dT%H:%M:%S`` (e.g. *2019-09-07T13:04:15*).
            An int or float is assumed to represent a Unix timestamp.  All datetime inputs are assumed to be UTC.
        :type to: str or datetime.datetime or datetime.date or int or float or None

        :param language: The 2-letter ISO-639-1 code of the language you want to get headlines for.
            See :data:`newsapi.const.languages` for the set of allowed values.
        :type language: str or None

        :param sort_by: The order to sort articles in.
            See :data:`newsapi.const.sort_method` for the set of allowed values.
        :type sort_by: str or None

        :param page: The number of results to return per page (request).
            20 is the default, 100 is the maximum.
        :type page: int or None

        :param page_size: Use this to page through the results if the total results found is
            greater than the page size.
        :type page_size: int or None

        :return: JSON response as nested Python dictionary.
        :rtype: dict
        :raises NewsAPIException: If the ``"status"`` value of the response is ``"error"`` rather than ``"ok"``.
        """
        # Clean up the parameters to ensure int is int
        if page_size is not None:
            page_size = int(page_size)
        if page is not None:
            page = int(page)
        else:
            page = 5
        return self.newsapi_client.get_everything(
            q=q,
            qintitle=qintitle,
            sources=sources,
            domains=domains,
            exclude_domains=exclude_domains,
            from_param=from_param,
            to=to,
            language=language,
            sort_by=sort_by,
            page_size=page_size,
            page=page,
        )
