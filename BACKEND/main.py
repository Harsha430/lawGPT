"""
Main entry point for the LawGPT application.
"""
import os
import sys
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.settings import (
    DEFAULT_PDF_PATH, BOOKS_DIR, API_PORT, API_HOST
)
from utils.helpers import print_colored, print_header, check_environment

# Load environment variables
load_dotenv()

# Global variables for use across the application
retriever = None
docs = None

def init_app():
    """Initialize the FastAPI application"""
    app = FastAPI(title="LawGPT API", description="Legal research assistant API")
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # For development only; restrict in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include API routes
    from api.routes import router
    app.include_router(router)
    
    return app

def load_pdf():
    """Load and process the PDF file"""
    global retriever, docs
    
    # Check if PDF exists, otherwise use a default from the books directory
    pdf_path = DEFAULT_PDF_PATH
    if not os.path.exists(pdf_path):
        # Try to find a PDF in the books directory
        if os.path.exists(BOOKS_DIR):
            pdf_files = [f for f in os.listdir(BOOKS_DIR) if f.endswith('.pdf')]
            if pdf_files:
                pdf_path = os.path.join(BOOKS_DIR, pdf_files[0])
                print_colored(f"Using PDF from books directory: {pdf_path}", "yellow")
    
    # Process the PDF and create vector database
    print_colored(f"Processing PDF: {pdf_path}", "yellow")
    from services.pdf_service import process_pdf
    docs, pdf_hash = process_pdf(pdf_path)
    
    if docs and pdf_hash:
        # Create or load vector database and retriever
        from services.vector_db_service import create_or_load_vector_db
        retriever, _ = create_or_load_vector_db(docs, pdf_hash)
        if retriever:
            print_colored("✓ System ready to process questions", "green")
            return True
    
    print_colored("Failed to initialize system", "red")
    return False

# Check environment variables
if os.environ.get("INITIALIZE_APP", "true").lower() == "true":
    print_header()
    if not check_environment(["GOOGLE_API_KEY"]):
        sys.exit(1)
    
    # Initialize the application
    app = init_app()
    
    # Load PDF at startup - this needs to happen before the app starts
    if not load_pdf():
        print_colored("Error: Could not load PDF or initialize vector database", "red")
        sys.exit(1)
else:
    # Just initialize the app without loading PDF (for importing)
    app = init_app()