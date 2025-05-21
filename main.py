import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agent import query_agent

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(
    title="LLM GraphQL Agent",
    description="API for querying GraphQL using natural language",
    version="1.0.0"
)

class QueryRequest(BaseModel):
    question: str

@app.get("/")
async def root():
    """
    Root endpoint with basic information
    """
    return {
        "service": "LLM GraphQL Agent",
        "version": "1.0.0",
        "usage": "Send POST requests to /query with JSON body {\"question\": \"your question\"}"
    }

@app.get("/health")
async def health_check():
    """
    Simple health check endpoint
    """
    return {"status": "healthy"}

@app.post("/query")
async def query(request: QueryRequest):
    """
    Process a natural language query and convert it to GraphQL
    """
    if not request.question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    logger.info(f"Received query: {request.question}")
    
    try:
        answer = query_agent(request.question)
        return {"answer": answer}
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)