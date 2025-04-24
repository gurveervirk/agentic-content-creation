import os
import logging
from typing import Optional, List, Dict, Any
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from llama_index.core.workflow import Context

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

SCOPES = ['https://www.googleapis.com/auth/blogger']
CLIENT_SECRETS_FILE = './secrets/credentials.json'
TOKEN_FILE = './secrets/token.json'

def get_blogger_service() -> Optional[Any]:
    """Authenticates the user with Google using OAuth 2.0 and returns a Blogger API v3 service object.

    Handles token loading, validation, refresh, and the initial authorization flow
    using 'client_secrets.json'. Stores/updates credentials in 'token.json'.

    Requires 'client_secrets.json' (renamed from Google Cloud Console credentials.json)
    and 'token.json' (created automatically) in the './secrets/' directory.

    Returns:
        Optional[googleapiclient.discovery.Resource]: The authenticated Blogger service object,
                                                     or None if authentication fails.
    """
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                logging.error(f"Error refreshing token: {e}")
                flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
                creds = flow.run_local_server(port=0)
        else:
            if not os.path.exists(CLIENT_SECRETS_FILE):
                logging.error(f"Error: {CLIENT_SECRETS_FILE} not found. Please download it from Google Cloud Console.")
                return None
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('blogger', 'v3', credentials=creds)
        return service
    except HttpError as error:
        logging.error(f'An error occurred building the service: {error}')
        return None
    except Exception as e:
        logging.error(f'An unexpected error occurred: {e}')
        return None

def fetch_user_blogs() -> Optional[List[Dict[str, Any]]]:
    """Fetches the list of blogs associated with the authenticated user's account.

    Uses the authenticated service obtained from get_blogger_service().
    Calls the Blogger API v3 'blogs.listByUser' method with userId='self'.

    Returns:
        Optional[List[Dict[str, Any]]]: A list of dictionaries, where each dictionary
                                        represents a blog (containing keys like 'id', 'name', 'url').
                                        Returns an empty list if no blogs are found.
                                        Returns None if the service is unavailable or an API error occurs.
    """
    service = get_blogger_service()
    if not service:
        return None
    try:
        blogs = service.blogs().listByUser(userId='self').execute()
        logging.info("Available blogs:")
        if 'items' in blogs:
            for blog in blogs['items']:
                logging.info(f"- {blog['name']} (ID: {blog['id']})")
            return blogs['items']
        else:
            logging.info("No blogs found for this user.")
            return []
    except HttpError as error:
        logging.error(f'An error occurred fetching blogs: {error}')
        return None

def search_blog_posts(blog_id: str, query: str) -> Optional[List[Dict[str, Any]]]:
    """Searches for posts within a specific blog that match a given query string.

    Uses the authenticated service obtained from get_blogger_service().
    Calls the Blogger API v3 'posts.search' method.

    Args:
        blog_id (str): The ID of the blog to search within.
        query (str): The search query string.

    Returns:
        Optional[List[Dict[str, Any]]]: A list of dictionaries, where each dictionary
                                        represents a matching post (containing keys like 'id', 'title', 'url').
                                        Returns an empty list if no posts match the query.
                                        Returns None if the service is unavailable or an API error occurs.
    """
    service = get_blogger_service()
    if not service:
        return None
    try:
        posts = service.posts().search(blogId=blog_id, q=query).execute()
        logging.info(f"Search results for '{query}' in blog ID {blog_id}:")
        if 'items' in posts:
            for post in posts['items']:
                logging.info(f"- {post['title']} (ID: {post['id']})")
            return posts['items']
        else:
            logging.info("No matching posts found.")
            return []
    except HttpError as error:
        logging.error(f'An error occurred searching posts: {error}')
        return None

def create_blog_post(blog_id: str, title: str, content_html: str) -> Optional[Dict[str, Any]]:
    """Creates a new blog post on a specified blog.

    Uses the authenticated service obtained from get_blogger_service().
    Calls the Blogger API v3 'posts.insert' method.
    Should typically be called *after* user confirmation via the ManagerAgent.

    Args:
        blog_id (str): The ID of the blog where the post will be created.
        title (str): The title for the new blog post.
        content_html (str): The HTML content for the new blog post.

    Returns:
        Optional[Dict[str, Any]]: A dictionary representing the newly created post
                                  (containing keys like 'id', 'title', 'url', 'published', 'updated').
                                  Returns None if the service is unavailable or an API error occurs.
    """
    service = get_blogger_service()
    if not service:
        return None
    try:
        post_body = {
            "title": title,
            "content": content_html
        }
        post = service.posts().insert(blogId=blog_id, body=post_body).execute()
        logging.info(f"Successfully created post:")
        logging.info(f"- Title: {post['title']}")
        logging.info(f"- ID: {post['id']}")
        logging.info(f"- URL: {post['url']}")
        return post
    except HttpError as error:
        logging.error(f'An error occurred creating the post: {error}')
        return None
    
def update_blog_post(blog_id: str, post_id: str, title: str, content_html: str) -> Optional[Dict[str, Any]]:
    """Updates an existing blog post with a new title and/or content.

    Uses the authenticated service obtained from get_blogger_service().
    Calls the Blogger API v3 'posts.update' method.
    Should typically be called *after* user confirmation via the ManagerAgent.

    Args:
        blog_id (str): The ID of the blog containing the post.
        post_id (str): The ID of the post to update.
        title (str): The new title for the blog post.
        content_html (str): The new HTML content for the blog post.

    Returns:
        Optional[Dict[str, Any]]: A dictionary representing the updated post
                                  (containing keys like 'id', 'title', 'url', 'published', 'updated').
                                  Returns None if the service is unavailable or an API error occurs.
    """
    service = get_blogger_service()
    if not service:
        return None
    try:
        post_body = {
            "title": title,
            "content": content_html
        }
        post = service.posts().update(blogId=blog_id, postId=post_id, body=post_body).execute()
        logging.info(f"Successfully updated post:")
        logging.info(f"- Title: {post['title']}")
        logging.info(f"- ID: {post['id']}")
        logging.info(f"- URL: {post['url']}")
        return post
    except HttpError as error:
        logging.error(f'An error occurred updating the post: {error}')
        return None
    
def delete_blog_post(blog_id: str, post_id: str) -> None:
    """Deletes a specific blog post.

    Uses the authenticated service obtained from get_blogger_service().
    Calls the Blogger API v3 'posts.delete' method.
    Should typically be called *after* user confirmation via the ManagerAgent.

    Args:
        blog_id (str): The ID of the blog containing the post.
        post_id (str): The ID of the post to delete.

    Returns:
        None. Logs success or error messages.
    """
    service = get_blogger_service()
    if not service:
        return None
    try:
        service.posts().delete(blogId=blog_id, postId=post_id).execute()
        logging.info(f"Successfully deleted post with ID: {post_id}")
    except HttpError as error:
        logging.error(f'An error occurred deleting the post: {error}')
        return None

async def prepare_blog_post(ctx: Context, title: str, content_html: str) -> str:
    """Stores proposed blog post title and content into the workflow context for confirmation.

    This function DOES NOT interact with the Blogger API. It prepares the data
    so the ManagerAgent can present it to the user for approval before calling
    `create_blog_post` or `update_blog_post`.

    Args:
        ctx (Context): The LlamaIndex workflow context object.
        title (str): The proposed title of the blog post.
        content_html (str): The proposed HTML content of the blog post.

    Returns:
        str: A status message indicating success ("Blog post prepared in context.")
             or failure ("Failed to prepare blog post in context.").
    """
    try:
        state = await ctx.get("state")
        state["blog_post"] = {
            "title": title,
            "content_html": content_html
        }
        return "Blog post prepared in context."
    except Exception as e:
        logging.error(f"Error preparing blog post in context: {e}")
        return "Failed to prepare blog post in context."
    
async def read_prepared_blog_post(ctx: Context) -> Dict[str, str] | str:
    """Reads the prepared blog post data (title and content) from the workflow context.

    This function DOES NOT interact with the Blogger API. It retrieves the data
    previously stored by `prepare_blog_post` from the context state.
    Used by the ManagerAgent to display the proposed post to the user for confirmation.

    Args:
        ctx (Context): The LlamaIndex workflow context object.

    Returns:
        Dict[str, str] | str: A dictionary containing the 'title' and 'content_html'
                               of the prepared blog post, or an error message string if
                               retrieval fails or no post is prepared.
    """
    try:
        state = await ctx.get("state")
        blog_post = state.get("blog_post", {})
        return blog_post or "No blog post prepared in context."
    except Exception as e:
        logging.error(f"Error reading prepared blog post from context: {e}")
        return "Failed to read blog post from context."