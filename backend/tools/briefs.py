from llama_index.core.workflow import Context

async def write_intel_briefing(ctx: Context, intel_briefing: str, key: str) -> str:
    """
    Write the intel briefing in the context, under the given key.

    Args:
        ctx (Context): The context object.
        intel_briefing (str): The intel briefing to set.
        key (str): The key under which to set the intel briefing.

    Returns:
        str: Status message indicating the intel briefing has been set.
    """
    try:
        state = await ctx.get("state")

        if "intel_briefing" not in state:
            state["intel_briefing"] = {}

        state["intel_briefing"][key] = intel_briefing
        await ctx.set("state", state)
        return f"Intel briefing set under key: {key}"
    
    except Exception as e:
        return f"Error setting intel briefing: {str(e)}"
    
async def get_intel_briefing(ctx: Context, key: str) -> str:
    """
    Get the intel briefing from the context, under the given key.

    Args:
        ctx (Context): The context object.
        key (str): The key under which the intel briefing is stored.

    Returns:
        str: The intel briefing if found, otherwise an error message.
    """
    try:
        state = await ctx.get("state")
        intel_briefing = state.get("intel_briefing", {}).get(key, None)

        if intel_briefing is not None:
            return intel_briefing
        else:
            return f"No intel briefing found under key: {key}"
    
    except Exception as e:
        return f"Error retrieving intel briefing: {str(e)}"