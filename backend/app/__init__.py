import logging
from .models import ChatRequest, ChatResponse
from .workflow import Workflow
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables from .env file
load_dotenv("./secrets/.env")

# Set up CORS middleware
origins = ["*"]  # Allow all origins for simplicity; adjust as needed

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

wflw = Workflow()

# Add /api prefix to all routes
app = FastAPI(
    title="Agent Workflow API",
    root_path="/api",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    try:
        response = await wflw.chat(request.message)
        return ChatResponse(response=response)
    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")
    
@app.post("/reset")
async def reset() -> dict[str, str]:
    try:
        await wflw.reset_context()
        return {"message": "Workflow reset successfully."}
    except Exception as e:
        logging.error(f"Error resetting workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error resetting workflow: {str(e)}")


@app.get("/get-contexts")
async def get_contexts() -> dict:
    try:
        contexts = wflw.ctx_index
        # Convert contexts dict to a proper string format if it's not already
        return {"contexts": str(contexts) if contexts else "{}"}
    except Exception as e:
        logging.error(f"Error retrieving contexts: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving contexts: {str(e)}")
    
@app.post("/load-context")
async def load_context(id: str) -> dict:
    try:
        chat_history = await wflw.load_context(id)
        if chat_history is None:
            raise HTTPException(status_code=404, detail="Context not found.")
        return {"chat_history": chat_history}
    except Exception as e:
        logging.error(f"Error loading context: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error loading context: {str(e)}")

@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Welcome to the Agent Workflow API"}