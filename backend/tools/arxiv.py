from llama_index.tools.arxiv import ArxivToolSpec

def arxiv_query(query: str, sort_by: str):
    """
    A tool to query arxiv.org
    ArXiv contains a variety of papers that are useful for answering
    mathematic and scientific questions.

    Args:
        query (str): The query to be passed to arXiv.
        sort_by (str): Either 'relevance' (default) or 'recent'

    """
    arxiv_tool = ArxivToolSpec()
    return arxiv_tool.arxiv_query(query, sort_by=sort_by)