# Render Chat Flow - Backend

## Overview

The backend for Render Chat Flow provides the AI-powered chat functionality and serves as the API for the frontend application. Built using Python, it orchestrates AI workflows, manages contextual memory, and integrates with various external knowledge tools.

## Technology Stack

- **Python 3.10+**: Core programming language
- **FastAPI/Flask** (implied): Web framework for API endpoints
- **LLM Integration**: Integration with large language models (Gemini)
- **External API Integrations**: Tools for various knowledge sources

## Project Structure

```
backend/
│
├── app/
│   ├── __init__.py      # Package initialization
│   ├── models.py        # Data models and schemas
│   └── workflow.py      # Core workflow logic
│
├── tools/               # AI tool integrations
│   ├── __init__.py
│   ├── arxiv.py         # arXiv paper search and analysis
│   ├── blog.py          # Blog content retrieval
│   ├── briefs.py        # Content summarization
│   ├── duckduckgo.py    # Web search functionality
│   ├── news.py          # News article retrieval
│   ├── wikipedia.py     # Wikipedia knowledge integration
│   └── youtube.py       # YouTube content access
│
├── prompts.py           # AI prompt templates
├── requirements.txt     # Python dependencies
│
└── secrets/             # API keys and credentials (not in source control)
    ├── credentials.json
    └── token.json
```

## Core Components

### Workflow Management

The `workflow.py` file contains the main orchestration logic that:

- Manages conversation state and history
- Routes user queries to appropriate tools
- Maintains context between interactions
- Formats responses for the frontend

### Data Models

The `models.py` file defines the data structures used throughout the application:

- Message schemas
- Tool configurations
- Workflow state representations
- API response formats

### External Tool Integrations

The `tools/` directory contains modules for integrating with various external APIs and services:

- **arxiv.py**: Searches and retrieves scientific papers from arXiv
- **wikipedia.py**: Fetches and processes content from Wikipedia
- **news.py**: Retrieves current news articles from news sources
- **duckduckgo.py**: Performs web searches through DuckDuckGo
- **youtube.py**: Accesses and processes YouTube video content
- **blog.py**: Retrieves and processes blog content
- **briefs.py**: Creates summarized versions of content

Each tool follows a consistent interface for seamless integration into the workflow system.

### Prompt Engineering

The `prompts.py` file contains carefully crafted templates for interacting with the underlying language model:

- System instructions
- Tool usage guidelines
- Response formatting directives
- Conversation management templates

## API Endpoints

The backend exposes several API endpoints:

- **POST /api/chat**: Process user messages and generate responses
- **POST /api/reset**: Reset the conversation state

## Authentication and Secrets

The `secrets/` directory contains authentication credentials for various services:

- **credentials.json**: API keys for external services
- **token.json**: Authentication tokens
- **.env**: Environment variables for local development

> **Note**: These files should never be committed to version control and are included in `.gitignore`.

## Workflow Process

1. User message is received from the frontend
2. The workflow processor analyzes the message intent
3. Appropriate tools are selected based on the query
4. External knowledge is gathered if needed
5. The language model generates a response using the gathered context
6. The response is formatted and returned to the frontend

## Development Setup

1. **Environment Setup**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Secrets Configuration**:

   - Create a `secrets/credentials.json` file with necessary API keys
   - Create a `secrets/.env` file for environment variables
   - Format should follow the application's expected structure

3. **Running the Server**:
   ```bash
   uvicorn app:app
   ```

## Tool Development

To create a new tool integration:

1. Create a new file in the `tools/` directory
2. Implement the common tool interface (likely with `get` and `execute` methods)
3. Register the tool in the tool manager
4. Add appropriate prompt templates in `prompts.py`
