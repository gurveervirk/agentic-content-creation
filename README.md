# Agentic Content Creator

## Project Overview

Agentic Content Creator is a full-stack application that provides an interactive chat interface with AI capabilities. The application consists of a React-based frontend for the user interface and a Python-based backend for handling chat logic and integrating with AI services.

## Architecture

The project follows a modern client-server architecture:

```
render-chat-flow/
│
├── frontend/ - React/TypeScript SPA built with Vite
│   ├── src/ - Frontend source code
│   ├── public/ - Static assets
│   └── ... - Configuration files
│
└── backend/ - Python-based API server
    ├── app/ - Core application logic
    ├── tools/ - AI tool integrations
    ├── prompts.py - AI prompt templates
    └── secrets/ - Configuration and credentials (not committed to source control)
```

## Key Features

- **Interactive Chat Interface**: Clean, responsive UI for real-time conversations
- **Workflow-based AI Processing**: Structured application workflow for AI processing
- **Tool Integration**: Multiple knowledge sources including Wikipedia, arXiv, news and more
- **Theming**: Custom theming with a purple-based color scheme

## Getting Started

### Prerequisites

- Node.js 16+ and npm/bun for frontend
- Python 3.10+ for backend
- API keys for any external services (stored in secrets/)

### Running the Application

1. **Frontend**:

   ```bash
   cd frontend
   npm install
   npm run dev
   ```

2. **Backend**:
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn app:app
   ```

## Project Structure Details

For more detailed information about the individual components, please refer to:

- [Frontend Documentation](./frontend/README.md)
- [Backend Documentation](./backend/README.md)

## Development

This project was created with modern development practices in mind:

- TypeScript for type safety
- React for UI components
- shadcn/ui and TailwindCSS for styling
- Python for backend services
