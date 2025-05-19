"""
LLM service for LawGPT application.
"""
import pickle
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from config.settings import (
    LLM_MODEL, TEMPERATURE, MAX_OUTPUT_TOKENS, TOP_K, TOP_P, HISTORY_FILE
)
from utils.helpers import print_colored


# Global variable to store conversation history
conversation_history = []


def save_history():
    """Save conversation history to file"""
    with open(HISTORY_FILE, "wb") as f:
        pickle.dump(conversation_history, f)


def load_history():
    """Load conversation history from file"""
    global conversation_history
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "rb") as f:
                conversation_history = pickle.load(f)
        except Exception as e:
            print_colored(f"Error loading history: {e}", "red")
            conversation_history = []


# Load history at module initialization
load_history()


def determine_response_style(question):
    """Determine the appropriate response style based on the question type"""
    question = question.lower()
    
    if any(word in question for word in ["summary", "overview", "summarize"]):
        return "summary"
    elif any(word in question for word in ["list", "steps", "how to", "process", "steps"]):
        return "list"
    elif any(word in question for word in ["compare", "difference", "similar", "versus", "vs"]):
        return "comparison"
    elif any(word in question for word in ["why", "reason", "explain", "rationale"]):
        return "explanation"
    elif any(word in question for word in ["what is", "define", "meaning", "concept"]):
        return "definition"
    elif any(word in question for word in ["precedent", "ruling", "decision"]):
        return "case_ruling"
    elif any(word in question for word in ["statute", "law", "regulation"]):
        return "legal_reference"
    elif any(word in question for word in ["judges", "justice", "bench"]):
        return "court_composition"
    else:
        return "general"


def get_llm_response(user_question, retriever):
    """Get response from LLM using retrieval chain"""
    try:
        # Add conversation history context
        history_text = ""
        for i, (q, a) in enumerate(conversation_history[-3:]):  # Use last 3 conversations for context
            history_text += f"Q{i+1}: {q}\nA{i+1}: {a}\n\n"

        response_style = determine_response_style(user_question)

        # Create LLM with model
        llm = ChatGoogleGenerativeAI(
            model=LLM_MODEL,
            temperature=TEMPERATURE,
            max_output_tokens=MAX_OUTPUT_TOKENS,
            top_k=TOP_K,
            top_p=TOP_P
        )

        # Create prompt template
        system_prompt = f"""You are a friendly, helpful legal research assistant for law students and the public.
Use the following legal case documents and conversation history to answer questions.

Conversation History:
{history_text}

Context: {{context}}

Current Question: {user_question}
Detected Response Style: {response_style}

Guidelines:
- Always be friendly and supportive.
- Provide accurate, clear, and concise legal information.
- Reference previous questions and answers if relevant.
- If you don't know, say so honestly with "I don't know" or "Not found in the provided documents".
"""

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}")
        ])

        # Create chains
        question_answer_chain = create_stuff_documents_chain(llm, prompt)
        rag_chain = create_retrieval_chain(retriever, question_answer_chain)

        # Get response
        response = rag_chain.invoke({"input": user_question})
        answer = response["answer"]

        # Store the Q&A in history
        conversation_history.append((user_question, answer))
        save_history()

        return answer

    except Exception as e:
        error_message = f"Error generating response: {str(e)}"
        print_colored(error_message, "red")
        return error_message