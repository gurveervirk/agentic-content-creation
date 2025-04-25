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
from llama_index.core.workflow import Context
from datetime import datetime
from tools import news, youtube, blog, duckduckgo, briefs, arxiv, wikipedia, manager
from prompts import (
    ARXIV_AGENT_PROMPT,
    MANAGER_AGENT_PROMPT,
    DUCKDUCKGO_AGENT_PROMPT,
    NEWS_AGENT_PROMPT,
    WIKIPEDIA_AGENT_PROMPT,
    YOUTUBE_AGENT_PROMPT,
    BLOG_AGENT_PROMPT,
    BRIEF_WRITER_AGENT_PROMPT,
    TITLE_GEN_PROMPT
)
import json
import os
import logging
import asyncio
from uuid import uuid4

# Configure logging
logger = logging.getLogger(__name__)

# Helper function to run a coroutine in the background and log errors
async def _run_and_log_errors(coro, task_name="Background task"):
    """Runs a coroutine and logs any exceptions."""
    try:
        await coro
    except Exception:
        logger.exception(f"{task_name} failed.")

class Workflow():
    def __init__(self):        
        Settings.llm = GoogleGenAI(
            api_key=os.getenv("GEMINI_API_KEY"),
            temperature=1.0
        )
        self.title_gen_llm = GoogleGenAI(
            model="gemini-2.0-flash-lite",
            api_key=os.getenv("GEMINI_API_KEY"),
            temperature=0.1,
        )
        self.news_obj = news.News()
        self.tools = self.create_tools()
        self.agents = self.create_agents()
        self.workflow = AgentWorkflow(
            agents=self.agents,
            root_agent="ManagerAgent",
        )
        self.ctx = None
        self.ctx_id = None
        self.ctx_index = self.load_contexts_index()
        self.reverse_ctx_index = {v: k for k, v in self.ctx_index.items()}
        self.chat_history = None

    def load_contexts_index(self):
        """
        Loads the contexts index from the `contexts` directory.

        Args:
            None
        Returns:
            dict: A dictionary containing the context IDs and their corresponding titles.
        """
        try:
            # If the directory and the index file don't exist, create them
            if not os.path.exists("./contexts"):
                os.makedirs("./contexts")
            if not os.path.exists("./contexts/index.json"):
                with open("./contexts/index.json", "w") as f:
                    json.dump({}, f)

            ctx_index = {}
            
            # Load the index file
            with open("./contexts/index.json", "r") as f:
                ctx_index = json.load(f)

            # Check if the index is empty
            if not ctx_index:
                logger.info("Contexts index is empty.")
                return {}
            
            return ctx_index
        except FileNotFoundError:
            logger.warning("Contexts index file not found. Creating a new one.")
            return {}
        except json.JSONDecodeError:
            logger.error("Error decoding JSON from contexts index file. Creating a new one.")
            return {}

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
        get_blop_post_titles_tool = FunctionTool.from_defaults(
            fn=blog.get_blop_post_titles,
            name="GetBlogPostTitlesTool",
            description="Get the titles of all blog posts.",
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
        review_content_tool = FunctionTool.from_defaults(
            fn=manager.review_content,
            name="ReviewContentTool",
            description="Review the content of a specific type and key in the context.",
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
            get_blop_post_titles_tool,
        ]
        manager_tools = [
            youtube_video_script_reader_tool,
            read_prepared_blog_post_tool,
            review_content_tool,
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
            can_handoff_to=["NewsAgent", "YoutubeAgent", "ArxivAgent", "DuckDuckGoAgent", "WikipediaAgent", "BlogAgent"],
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
            brief_writer_agent,
            manager_agent,
        ]
    
    async def update_stored_context(self):
        """
        Updates the stored context in the `contexts` directory.
        Generates a title if it's a new context.
        """
        try:
            if self.ctx is None:
                raise ValueError("Handler context is not set. Cannot update stored context.")
            
            if self.ctx_id is None:
                # Generate title and update index, using the chat history
                title = await self.generate_title(self.chat_history)
                self.ctx_id = str(uuid4())
                self.reverse_ctx_index[title] = self.ctx_id
                self.ctx_index[self.ctx_id] = title
                with open("./contexts/index.json", "w") as f:
                    json.dump(self.ctx_index, f)
                logger.info(f"Title generated: {title}")

            elif self.ctx_index[self.ctx_id] is None:
                # Generate title and update index
                title = await self.generate_title(self.chat_history)
                self.reverse_ctx_index[title] = self.ctx_id
                self.ctx_index[self.ctx_id] = title
                with open("./contexts/index.json", "w") as f:
                    json.dump(self.ctx_index, f)
                logger.info(f"Title generated: {title}")
            
            context = self.ctx.to_dict()
            
            # Create the directory if it doesn't exist
            context_dir = f"./contexts/{self.ctx_id}"
            os.makedirs(context_dir, exist_ok=True)

            # Save the context to a single JSON file
            with open(f"{context_dir}/ctx.json", "w") as f:
                json.dump(context, f)

            # Save the chat history to a separate JSON file
            with open(f"{context_dir}/chat_history.json", "w") as f:
                json.dump(self.chat_history, f)
            
            logger.info(f"Context updated successfully: {self.ctx_id}")
        except Exception as e:
            logger.error(f"Error updating context: {e}")
            raise e
    
    async def chat(self, message: str) -> str:
        """Process a user message through the agent workflow."""
        try:
            if self.chat_history is None:
                self.chat_history = []

            # Append the user message to the chat history
            self.chat_history.append(message)
            current_agent = None
            
            handler = self.workflow.run(
                ctx=self.ctx,
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
            self.ctx = handler.ctx

            if complete_response is None:
                # If no response was generated, return a default message
                complete_response = "I'm sorry, I couldn't process your request."

            # Clean up the response to remove any "assistant:" prefixes
            elif complete_response.startswith("assistant: "):
                complete_response = complete_response[len("assistant: "):]

            self.chat_history.append(complete_response)

            # Update the stored context asynchronously
            update_coro = self.update_stored_context()
            asyncio.create_task(_run_and_log_errors(asyncio.shield(update_coro), "Context Update"))

            return complete_response or "I'm sorry, I couldn't process your request."
            
        except Exception as e:
            logger.error(f"Error in agent workflow: {str(e)}")
            return f"I encountered an error while processing your request: {str(e)}"

    async def reset_context(self):
        """
        Resets the chat context and agent workflow.
        """
        # If the context is not None, save it to the context file
        if self.ctx is not None:
            try:
                # Get the context and save it to a file
                context = self.ctx.to_dict()
                with open(f"contexts/{self.ctx_id}/ctx.json", "w") as f:
                    json.dump(context, f)

                with open(f"contexts/{self.ctx_id}/chat_history.json", "w") as f:
                    json.dump(self.chat_history, f)
            except Exception as e:
                logger.error(f"Error saving context: {e}")

        self.ctx = None
        self.ctx_id = None
        self.chat_history = None
        Settings.llm = GoogleGenAI(
            api_key=os.getenv("GEMINI_API_KEY"),
            temperature=1.0
        )
        self.agents = self.create_agents()
        self.workflow = AgentWorkflow(
            agents=self.agents,
            root_agent="ManagerAgent",
        )

    async def load_context(self, id: str) -> list[str]:
        """
        Loads the context for the agent workflow, from `contexts` directory.

        Args:
            ctx: The context to load.
        Returns:
            list[str]: A list of strings representing the chat history.
        """
        try:
            if id not in self.ctx_index:
                raise ValueError(f"Context with id {id} not found.")
            
            # Reset the current context, then load the new context
            await self.reset_context()

            context = json.load(open(f"./contexts/{id}/ctx.json", "r"))
            self.chat_history = json.load(open(f"./contexts/{id}/chat_history.json", "r"))

            # Create a new context
            self.ctx = Context.from_dict(
                workflow=self.workflow,
                data=context,
            )

            self.ctx_id = id
            logger.info(f"Context loaded successfully: {self.ctx_id}")

            return self.chat_history
            
        except Exception as e:
            logger.error(f"Error loading context: {e}")
            raise e
        
    async def generate_title(self, chat: list[str]) -> str:
        """
        Generate a title for the given chat using the LLM.

        Args:
            chat (list[str]): The chat history as a list of strings.
            
        Returns:
            str: The generated title.
        """

        try:
            # Format the chat history for the prompt
            chat = "\n".join([
                f"User: {message}" if i % 2 == 0 else f"AI: {message}"
                for i, message in enumerate(chat)
            ])
            prompt = TITLE_GEN_PROMPT.format(chat=chat)

            # Generate the title using the LLM
            title = await self.title_gen_llm.acomplete(
                prompt=prompt,
            )

            title = title.text.strip()

            # Extract the title from the response
            if title.startswith("<title>") and title.endswith("</title>"):
                title = title[7:-8].strip()
            else:
                raise ValueError("Invalid title format.")
            
            return None if title == "NONE" else title
        except Exception as e:
            logging.info(f"Error generating title: {e}")
            return None