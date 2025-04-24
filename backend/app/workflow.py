from llama_index.core.tools import FunctionTool
from llama_index.core import Settings
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.core.agent.workflow import (
    AgentOutput,
    ToolCall,
    ToolCallResult,
    AgentWorkflow,
    FunctionAgent
)
from datetime import datetime
from tools import news, youtube, blog, duckduckgo, briefs, arxiv, wikipedia
from prompts import (
    ARXIV_AGENT_PROMPT,
    MANAGER_AGENT_PROMPT,
    DUCKDUCKGO_AGENT_PROMPT,
    NEWS_AGENT_PROMPT,
    WIKIPEDIA_AGENT_PROMPT,
    YOUTUBE_AGENT_PROMPT,
    BLOG_AGENT_PROMPT,
    EDITOR_AGENT_PROMPT,
    BRIEF_WRITER_AGENT_PROMPT
)
import os
import logging

# Configure logging
logger = logging.getLogger(__name__)

class Workflow():
    def __init__(self):        
        Settings.llm = GoogleGenAI(
            # model="gemini-2.0-flash-lite",
            api_key=os.getenv("GEMINI_API_KEY"),
            temperature=1.0
        )
        self.news_obj = news.News()
        self.tools = self.create_tools()
        self.agents = self.create_agents()
        self.workflow = AgentWorkflow(
            agents=self.agents,
            root_agent="ManagerAgent",
        )
        self.handler = None

    def create_tools(self) -> dict[str, list[FunctionTool]]:
        news_articles_reader_tool = FunctionTool.from_defaults(
            fn=self.news_obj.read_news_articles,
            name="NewsArticlesReaderTool",
            description="Read news articles by passing their URL's",
        )
        news_headlines_search_tool = FunctionTool.from_defaults(
            fn=self.news_obj.get_top_headlines,
            name="NewsHeadlinesSearchTool",
            description="Get the latest news headlines",
        )
        news_sources_search_tool = FunctionTool.from_defaults(
            fn=self.news_obj.get_sources,
            name="NewsSourcesSearchTool",
            description="Fetch the subset of news publishers that /top-headlines are available from.",
        )
        news_everything_search_tool = FunctionTool.from_defaults(
            fn=self.news_obj.get_everything,
            name="NewsEverythingSearchTool",
            description="Get the latest news articles.",
        )
        youtube_videos_trancript_reader_tool = FunctionTool.from_defaults(
            fn=youtube.get_youtube_transcripts,
            name="YoutubeVideosTranscriptReaderTool",
            description="Read youtube video transcripts by passing their URL's",
        )
        youtube_video_script_writer_tool = FunctionTool.from_defaults(
            fn=youtube.write_video_script,
            name="YoutubeVideoScriptWriterTool",
            description="Write a youtube video script, by providing the video title and descriptive information.",
        )
        youtube_video_script_reader_tool = FunctionTool.from_defaults(
            fn=youtube.read_video_script,
            name="YoutubeVideoScriptReaderTool",
            description="Read a youtube video script from the context, set previously.",
        )
        fetch_user_blogs_tool = FunctionTool.from_defaults(
            fn=blog.fetch_user_blogs,
            name="FetchUserBlogsTool",
            description="Fetch the latest blogs from a user.",
        )
        search_blog_posts_tool = FunctionTool.from_defaults(
            fn=blog.search_blog_posts,
            name="SearchBlogPostsTool",
            description="Search blog posts by passing a query.",
        )
        prepare_blog_post_tool = FunctionTool.from_defaults(
            fn=blog.prepare_blog_post,
            name="PrepareBlogPostTool",
            description="Prepares blog post content (title, html) for user confirmation before actual creation or update. Returns a dict with a 'blog' key.",
        )
        read_prepared_blog_post_tool = FunctionTool.from_defaults(
            fn=blog.read_prepared_blog_post,
            name="ReadPreparedBlogPostTool",
            description="Reads the prepared blog post content (title, html) for user confirmation before actual creation or update.",
        )
        create_blog_post_tool = FunctionTool.from_defaults(
            fn=blog.create_blog_post,
            name="CreateBlogPostTool",
            description="Create a blog post by passing the title and content. Use ONLY after user confirmation via ManagerAgent.",
        )
        update_blog_post_tool = FunctionTool.from_defaults(
            fn=blog.update_blog_post,
            name="UpdateBlogPostTool",
            description="Update a blog post by passing the post ID and new content. Use ONLY after user confirmation via ManagerAgent.",
        )
        delete_blog_post_tool = FunctionTool.from_defaults(
            fn=blog.delete_blog_post,
            name="DeleteBlogPostTool",
            description="Deletes a blog post by passing the blog ID and post ID. Use ONLY after user confirmation via ManagerAgent.",
        )
        duckduckgo_instant_search_tool = FunctionTool.from_defaults(
            fn=duckduckgo.duckduckgo_instant_search,
            name="DuckDuckGoInstantSearchTool",
            description="Perform an instant search using DuckDuckGo.",
        )
        duckduckgo_full_search_tool = FunctionTool.from_defaults(
            fn=duckduckgo.duckduckgo_full_search,
            name="DuckDuckGoFullSearchTool",
            description="Perform a full search using DuckDuckGo.",
        )
        write_intel_briefing_tool = FunctionTool.from_defaults(
            fn=briefs.write_intel_briefing,
            name="WriteIntelBriefingTool",
            description="Write the intel briefing under a particular key, after researching the topic(s) or preparing content.",
        )
        get_intel_briefing_tool = FunctionTool.from_defaults(
            fn=briefs.get_intel_briefing,
            name="GetIntelBriefingTool",
            description="Get the intel briefing under a particular key.",
        )
        arxiv_query_tool = FunctionTool.from_defaults(
            fn=arxiv.arxiv_query,
            name="ArxivQueryTool",
            description="Get the latest arxiv papers.",
        )
        wikipedia_load_data_tool = FunctionTool.from_defaults(
            fn=wikipedia.load_data,
            name="WikipediaQueryTool",
            description="Load a Wikipedia page by passing the page title and language.",
        )
        wikipedia_search_data_tool = FunctionTool.from_defaults(
            fn=wikipedia.search_data,
            name="WikipediaSearchTool",
            description="Search Wikipedia for a page related to the given query.",
        )
        duckduckgo_search_tools = [
            duckduckgo_instant_search_tool,
            duckduckgo_full_search_tool,
        ]
        arxiv_query_tools = [arxiv_query_tool]
        wikipedia_query_tools = [
            wikipedia_load_data_tool,
            wikipedia_search_data_tool,
        ]
        youtube_tools = [
            youtube_videos_trancript_reader_tool,
            youtube_video_script_reader_tool,
            youtube_video_script_writer_tool,
            get_intel_briefing_tool,
        ]
        news_tools = [
            # news_articles_reader_tool,
            # news_headlines_search_tool,
            # news_sources_search_tool,
            news_everything_search_tool,
        ]
        blog_tools = [
            fetch_user_blogs_tool,
            search_blog_posts_tool,
            prepare_blog_post_tool,
            create_blog_post_tool,
            update_blog_post_tool,
            delete_blog_post_tool,
            read_prepared_blog_post_tool,
            get_intel_briefing_tool,
        ]
        manager_tools = [
            youtube_video_script_reader_tool,
            read_prepared_blog_post_tool,
        ]
        brief_writer_tools = [
            write_intel_briefing_tool
        ]
        tools = {
            "arxiv": arxiv_query_tools,
            "duckduckgo": duckduckgo_search_tools,
            "wikipedia": wikipedia_query_tools,
            "youtube": youtube_tools,
            "news": news_tools,
            "blog": blog_tools,
            "manager": manager_tools,
            "brief_writer": brief_writer_tools,
        }
        return tools

    def create_agents(self) -> list[FunctionAgent]:
        news_agent = FunctionAgent(
            name="NewsAgent",
            description="Get the latest news regarding a topic, read news articles, and get the latest news headlines.",
            tools=self.tools["news"],
            llm=Settings.llm,
            can_handoff_to=["ManagerAgent", "BriefWriterAgent"],
            system_prompt=NEWS_AGENT_PROMPT.format(
                current_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ),
        )
        youtube_agent = FunctionAgent(
            name="YoutubeAgent",
            description="Get youtube video transcripts and write video scripts",
            tools=self.tools["youtube"],
            llm=Settings.llm,
            can_handoff_to=["ManagerAgent", "BriefWriterAgent"],
            system_prompt=YOUTUBE_AGENT_PROMPT,
        )
        arxiv_agent = FunctionAgent(
            name="ArxivAgent",
            description="Get the latest arxiv papers",
            tools=self.tools["arxiv"],
            llm=Settings.llm,
            can_handoff_to=["ManagerAgent", "BriefWriterAgent"],
            system_prompt=ARXIV_AGENT_PROMPT,
        )
        duckduckgo_agent = FunctionAgent(
            name="DuckDuckGoAgent",
            description="Search the web using DuckDuckGo",
            tools=self.tools["duckduckgo"],
            llm=Settings.llm,
            can_handoff_to=["ManagerAgent", "BriefWriterAgent"],
            system_prompt=DUCKDUCKGO_AGENT_PROMPT,
        )
        wikipedia_agent = FunctionAgent(
            name="WikipediaAgent",
            description="Get the latest wikipedia articles",
            tools=self.tools["wikipedia"],
            llm=Settings.llm,
            can_handoff_to=["ManagerAgent", "BriefWriterAgent"],
            system_prompt=WIKIPEDIA_AGENT_PROMPT,
        )
        blog_agent = FunctionAgent(
            name="BlogAgent",
            description="Handles interactions with Blogger, including fetching, searching, preparing, creating, and updating posts.",
            tools=self.tools["blog"],
            llm=Settings.llm,
            can_handoff_to=["ManagerAgent", "BriefWriterAgent"],
            system_prompt=BLOG_AGENT_PROMPT,
        )
        editor_agent = FunctionAgent(
            name="EditorAgent",
            description="Review the blog post and youtube video script and provide feedback.",
            llm=Settings.llm,
            can_handoff_to=["ManagerAgent"],
            system_prompt=EDITOR_AGENT_PROMPT,
        )
        brief_writer_agent = FunctionAgent(
            name="BriefWriterAgent",
            description="Synthesizes raw research findings or stores prepared content into structured briefs using WriteIntelBriefingTool.",
            tools=self.tools["brief_writer"],
            llm=Settings.llm,
            can_handoff_to=["ManagerAgent"],
            system_prompt=BRIEF_WRITER_AGENT_PROMPT,
        )
        manager_agent = FunctionAgent(
            name="ManagerAgent",
            description="Manage the workflow, including user confirmation steps for actions.",
            llm=Settings.llm,
            tools=self.tools["manager"],
            can_handoff_to=["NewsAgent", "YoutubeAgent", "ArxivAgent", "DuckDuckGoAgent", "WikipediaAgent", "BlogAgent", "EditorAgent"],
            system_prompt=MANAGER_AGENT_PROMPT.format(
                current_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ),
        )
        return [
            news_agent,
            youtube_agent,
            arxiv_agent,
            duckduckgo_agent,
            wikipedia_agent,
            blog_agent,
            editor_agent,
            brief_writer_agent,
            manager_agent,
        ]
    
    async def chat(self, message: str) -> str:
        """Process a user message through the agent workflow."""
        try:
            current_agent = None
            
            ctx = self.handler.ctx if self.handler != None else None
            handler = self.workflow.run(
                ctx=ctx,
                user_msg=message
            )
            complete_response = None

            async for event in handler.stream_events():
                if (
                    hasattr(event, "current_agent_name")
                    and event.current_agent_name != current_agent
                ):
                    current_agent = event.current_agent_name
                    logging.info(f"🤖 Agent: {current_agent}")

                elif isinstance(event, AgentOutput):
                    if event.response.content:
                        logging.info("📤 Output: " + event.response.content)
                        complete_response = event.response.content
                    if event.tool_calls:
                        logging.info(
                            "🛠️  Planning to use tools: " +
                            str([call.tool_name for call in event.tool_calls]),
                        )
                elif isinstance(event, ToolCallResult):
                    logging.info(f"🔧 Tool Result ({event.tool_name}):")
                    logging.info(f"  Arguments: {event.tool_kwargs}")
                    logging.info(f"  Output: {event.tool_output}")
                elif isinstance(event, ToolCall):
                    logging.info(f"🔨 Calling Tool: {event.tool_name}")
                    logging.info(f"  With arguments: {event.tool_kwargs}")
            
            # Set the handler to the current handler for the next request
            self.handler = handler

            if complete_response is None:
                # If no response was generated, return a default message
                complete_response = "I'm sorry, I couldn't process your request."

            # Clean up the response to remove any "assistant:" prefixes
            if complete_response.startswith("assistant: "):
                complete_response = complete_response[len("assistant: "):]
            
                if current_agent != "ManagerAgent":
                    # If the last agent was not the manager agent, Reset the handler (FIX IN FUTURE)
                    self.handler = None

            return complete_response or "I'm sorry, I couldn't process your request."
            
        except Exception as e:
            logger.error(f"Error in agent workflow: {str(e)}")
            return f"I encountered an error while processing your request: {str(e)}"
        
    def reset(self) -> None:
        """Reset the workflow and its components."""
        Settings.llm = GoogleGenAI(
            # model="gemini-2.0-flash-lite",
            api_key=os.getenv("GEMINI_API_KEY"),
            temperature=1.0
        )
        self.agents = self.create_agents()
        self.workflow = AgentWorkflow(
            agents=self.agents,
            root_agent="ManagerAgent",
        )
        self.handler = None