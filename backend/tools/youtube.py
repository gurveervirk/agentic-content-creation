from llama_index.readers.youtube_transcript import YoutubeTranscriptReader
from llama_index.core import Settings
from llama_index.core.workflow import Context
from prompts import VIDEO_SCRIPT_WRITER_PROMPT

reader = YoutubeTranscriptReader()

def get_youtube_transcripts(links: list[str]) -> list[str]:
    """Get the transcripts of youtube videos."""
    documents = reader.load_data(ytlinks=links)
    transcripts = [doc.text for doc in documents]
    return transcripts

async def write_video_script(ctx: Context, title: str, information: str, intel_keys: list[str]) -> str:
    """
    Write a video script using the provided title and information, along with briefs provided in the intel keys.

    Args:
        ctx (Context): The context object.
        title (str): The title of the video.
        information (str): The information to be included in the script.
        intel_keys (list[str]): The intel keys to be used for generating the script.

    Returns:
        str: The generated video script.
    """
    try:
        intel_keys = intel_keys or []
        # Get the information from the context using the intel keys
        state = await ctx.get("state")
        # Check if `intel_briefing` exists in the context
        incorrect_keys = []
        if "intel_briefing" not in state:
            incorrect_keys = intel_keys
        else:
            incorrect_keys = [key for key in intel_keys if key not in state["intel_briefing"]]
        
        briefs = '\n\n'.join([f"{state['intel_briefing'][key]}" for key in intel_keys if key in state["intel_briefing"]])

        script = await Settings.llm.acomplete(
            prompt = VIDEO_SCRIPT_WRITER_PROMPT.format(
                briefs=briefs,
                title=title,
                information=information,
            ),
        )
        # Set the script in the context
        state = await ctx.get("state")
        state["script"] = script.text
        await ctx.set("state", state)

        result_str = script.text + "\n\nSuccessfully generated and set the video script in the context."
        if incorrect_keys:
            result_str += f"\n\nThe following keys were not found in the context: {', '.join(incorrect_keys)}"
            
        return result_str
    except Exception as e:
        return f"An error occurred while generating the video script: {str(e)}"

async def read_video_script(ctx: Context) -> str:
    """Read the video script from the context."""
    state = await ctx.get("state")
    return state["script"]