from llama_index.tools.wikipedia import WikipediaToolSpec

def load_data(
    page: str, lang: str
) -> str:
    """
    Retrieve a Wikipedia page. Useful for learning about a particular concept that isn't private information.

    Args:
        page (str): Title of the page to read.
        lang (str): Language of Wikipedia to read. (default: en)
    """
    wikipedia_tool = WikipediaToolSpec()
    return wikipedia_tool.load_data(page, lang)

def search_data(
    query: str, lang: str
) -> str:
    """
    Search Wikipedia for a page related to the given query.
    Use this tool when `load_data` returns no results.

    Args:
        query (str): the string to search for
        lang (str): Language of Wikipedia to read. (default: en)
    """
    wikipedia_tool = WikipediaToolSpec()
    return wikipedia_tool.search_data(query, lang)