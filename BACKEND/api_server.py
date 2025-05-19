from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from law import get_llm_response, process_pdf, DEFAULT_PDF_PATH

app = FastAPI()

# Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development only; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QuestionRequest(BaseModel):
    question: str

# Load PDF and create retriever once at startup
retriever, docs = process_pdf(DEFAULT_PDF_PATH)

@app.post("/api/ask")
async def ask_question(req: QuestionRequest):
    answer = get_llm_response(req.question, retriever)
    return {"answer": answer}