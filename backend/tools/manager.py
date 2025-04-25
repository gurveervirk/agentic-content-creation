from llama_index.core.workflow import Context
from llama_index.llms.google_genai import GoogleGenAI
from prompts import REVIEW_PROMPT
import os

async def review_content(
    ctx: Context,
    content_type: str,
    key: str,
) -> str:
    """
    Review the content of a specific type and key in the context.

    Args:
        ctx (Context): The context object containing the content.
        content_type (str): The type of content to review.
        key (str): The key of the content to review.

    Returns:
        str: The Review of the content.
    """
    try:
        if content_type not in ["blog_posts", "scripts"]:
            raise ValueError("Invalid content type. Must be 'blog_posts' or 'scripts'.")

        state = await ctx.get("state")

        if content_type not in state:
            raise ValueError(f"No {content_type} content found in the context. Please prepare it first.")
        
        content = state[content_type].get(key, None)

        if content is None: 
            return f"No {content_type} content found for the key '{key}'."

        # Prepare Review LLM
        review_llm = GoogleGenAI(
            model="gemini-2.0-flash-lite",
            api_key=os.getenv("GEMINI_API_KEY"),
        )

        review = await review_llm.acomplete(
            prompt=REVIEW_PROMPT.format(
                content_to_review=content,
            )
        )

        return review

    except Exception as e:
        raise ValueError(f"Error reviewing content: {str(e)}")
        