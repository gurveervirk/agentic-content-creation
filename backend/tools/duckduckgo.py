from llama_index.tools.duckduckgo import DuckDuckGoSearchToolSpec

def duckduckgo_instant_search(query: str) -> str:
    """Perform an instant search using DuckDuckGo."""
    return DuckDuckGoSearchToolSpec().duckduckgo_instant_search(query)

def duckduckgo_full_search(query: str, region: str, max_results: int) -> str:
    """Perform a full search using DuckDuckGo."""
    max_results = int(max_results)
    return DuckDuckGoSearchToolSpec().duckduckgo_full_search(query, region, max_results)