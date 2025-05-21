from fastapi import FastAPI
from pydantic import BaseModel
from agent import query_agent

app = FastAPI()

class QueryRequest(BaseModel):
    q: str

@app.post("/query")
async def query(request: QueryRequest):
    answer = query_agent(request.q)
    return {"answer": answer}
