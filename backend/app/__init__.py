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

app = FastAPI(title="Agent Workflow API")
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
        wflw.reset()
        return {"message": "Workflow reset successfully."}
    except Exception as e:
        logging.error(f"Error resetting workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error resetting workflow: {str(e)}")

@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Welcome to the Agent Workflow API"}