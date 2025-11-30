import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.documents import Document
from pinecone import Pinecone
from huggingface_hub import InferenceClient


load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
HF_API_KEY = os.getenv("HF_API_KEY")

INDEX_NAME = "lawgpt"
HF_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


app = FastAPI(title="RAG Chatbot API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)


llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=GOOGLE_API_KEY,
    temperature=0.1,  
    max_output_tokens=1800  
)


hf_client = InferenceClient(token=HF_API_KEY)

def embed_text(text: str):
    embedding = hf_client.feature_extraction(text, model=HF_MODEL)
    
    
    if isinstance(embedding[0], list):
        embedding = embedding[0]

    
    embedding = [float(x) for x in embedding]
    
    return embedding


pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(INDEX_NAME)


class QueryRequest(BaseModel):
    query: str
    conversation_history: list[dict] = []


def retrieve_docs(query: str):
    import re
    
    
    section_match = re.search(r'section\s+(\d+)', query.lower())
    
    if section_match:
        section_num = section_match.group(1)
        
       
        
        queries = [
            f"Section {section_num}",
            f"{section_num}. ",
            f"section {section_num} provisions penalties procedure evidence"
        ]
        
        all_matches = []
        seen_ids = set()
        
        
        for search_query in queries:
            query_vector = embed_text(search_query)
            results = index.query(
                vector=query_vector,
                top_k=200,  
                include_metadata=True
            )
            
            for match in results["matches"]:
                if match["id"] not in seen_ids:
                    seen_ids.add(match["id"])
                    all_matches.append(match)
        
        
        filtered_matches = []
        
        for match in all_matches:
            text = match["metadata"]["text"]
            text_lower = text.lower()
            
            
            
            is_match = False
            
            
            patterns = [
                rf'(^|\n)\s*{section_num}\.\s+',  
                rf'(^|\n){section_num}\.\s+[A-Z]',  
                rf'[a-zA-Z]\s*{section_num}\.',  
                rf'_+\s*{section_num}\.\s+',  
            ]
            
            for pattern in patterns:
                if re.search(pattern, text, re.MULTILINE):
                    is_match = True
                    break
            
            
            if not is_match:
                simple_checks = [
                    f"\n{section_num}. ",
                    f" {section_num}. the ",
                    f" {section_num}. whoever",
                    f"_{section_num}. ",
                ]
                for check in simple_checks:
                    if check in text_lower:
                        is_match = True
                        break
            
            if is_match:
                filtered_matches.append(match)
        
        
        results_to_use = filtered_matches if filtered_matches else all_matches[:50]
        
    else:
        
        query_vector = embed_text(query)
        results_to_use = index.query(
            vector=query_vector,
            top_k=50,
            include_metadata=True
        )["matches"]

    
    docs_by_source = {
        "BNS": [],
        "BNSS": [],
        "BSA": []
    }
    
    for match in results_to_use:
        text = match["metadata"]["text"]
        source = match["metadata"].get("source", "UNKNOWN")
        score = match["score"]
        
        if source in docs_by_source:
            docs_by_source[source].append({
                "text": text,
                "score": score
            })

    return docs_by_source


def rag_chat(query: str, conversation_history: list[dict] = None):
    docs_by_source = retrieve_docs(query)
    
    
    query_lower = query.lower()
    is_scenario = any(indicator in query_lower for indicator in [
        'if', 'can i', 'what happens', 'should i', 'is it legal', 'do i have to',
        'someone', 'a person', 'what if', 'suppose', 'scenario', 'case', 'situation'
    ])
    
    
    chunk_limit = 15 if is_scenario else 10
    
    
    context_parts = []
    
    
    if docs_by_source["BNS"]:
        bns_texts = [doc["text"] for doc in docs_by_source["BNS"][:chunk_limit]]
        context_parts.append("=== BNS (Bharatiya Nyaya Sanhita - Substantive Criminal Law) ===")
        context_parts.append("\n\n".join(bns_texts))
    
    
    if docs_by_source["BNSS"]:
        bnss_texts = [doc["text"] for doc in docs_by_source["BNSS"][:chunk_limit]]
        context_parts.append("\n\n=== BNSS (Bharatiya Nagarik Suraksha Sanhita - Criminal Procedure) ===")
        context_parts.append("\n\n".join(bnss_texts))
    
    
    if docs_by_source["BSA"]:
        bsa_texts = [doc["text"] for doc in docs_by_source["BSA"][:chunk_limit]]
        context_parts.append("\n\n=== BSA (Bharatiya Sakshya Adhiniyam - Evidence Law) ===")
        context_parts.append("\n\n".join(bsa_texts))
    
    context = "\n\n".join(context_parts)
    
    
    with open("system_prompt.txt", "r", encoding="utf-8") as f:
        prompt_template = f.read()
    
    
    conversation_context = ""
    if conversation_history:
        conversation_context = "\n\n=== PREVIOUS CONVERSATION ===\n"
        for msg in conversation_history[-16:]:  
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "user":
                conversation_context += f"User: {content}\n"
            elif role == "assistant":
                conversation_context += f"Assistant: {content}\n"
        conversation_context += "\n=== END OF PREVIOUS CONVERSATION ===\n\n"
    
    
    prompt = prompt_template.format(context=context, query=query)
    
    
    if conversation_context:
        prompt = prompt.replace("{query}", f"{conversation_context}Current Question: {{query}}")
        prompt = prompt.format(query=query)
    
    
    response = llm.invoke(prompt)
    return response.content


@app.post("/chat")
async def chat(request: QueryRequest):
    try:
        if not request.query or request.query.strip() == "":
            return {"response": "Please provide a valid question.", "error": True}
        
        answer = rag_chat(request.query, request.conversation_history)
        return {"response": answer, "error": False}
    except Exception as e:
        return {"response": f"An error occurred while processing your request. Please try again.", "error": True, "details": str(e)}

@app.get("/")
async def home():
    return {"message": "LawGPT API running successfully!", "status": "active", "version": "1.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint to verify API is running"""
    try:
        
        stats = index.describe_index_stats()
        return {
            "status": "healthy",
            "pinecone_connected": True,
            "total_vectors": stats.total_vector_count,
            "model": "gemini-2.5-flash",
            "embedding_model": HF_MODEL
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }