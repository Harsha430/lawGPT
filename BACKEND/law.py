import os
import sys
import pickle
from colorama import init, Fore, Style
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores import Qdrant
import requests  # For web search agent (optional, see below)

# Initialize colorama for cross-platform colored terminal text
init()

# Load environment variables
load_dotenv()

# Check if Google API key is set
if not os.getenv("GOOGLE_API_KEY"):
    print(f"{Fore.RED}Error: GOOGLE_API_KEY environment variable is not set.")
    print(f"Please create a .env file with your API key.{Style.RESET_ALL}")
    sys.exit(1)

# Default PDF path - can be overridden by command line argument
DEFAULT_PDF_PATH = r"C:\Users\91964\OneDrive\Desktop\law\BACKEND\ilovepdf_merged.pdf"

HISTORY_FILE = "conversation_history.pkl"

def print_colored(text, color=Fore.WHITE, bold=False):
    """Print colored text to terminal"""
    style = Style.BRIGHT if bold else ""
    print(f"{style}{color}{text}{Style.RESET_ALL}")

def print_header():
    """Print application header"""
    print("\n" + "="*60)
    print_colored("LEGAL CASE RESEARCH ASSISTANT", Fore.CYAN, bold=True)
    print_colored("Helping law students find relevant case information", Fore.CYAN)
    print("="*60 + "\n")

def process_pdf(pdf_path):
    """Process the PDF file and create a retriever"""
    print_colored(f"Processing PDF: {pdf_path}", Fore.YELLOW)
    
    try:
        # Load and split the PDF
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()
        
        print_colored(f"✓ Loaded {len(documents)} pages from PDF", Fore.GREEN)
        
        # Split the documents into chunks optimized for Gemini
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=2000,
            chunk_overlap=200,
            separators=["\n\n", "\n", " ", ""]
        )
        docs = text_splitter.split_documents(documents)
        
        print_colored(f"✓ Split into {len(docs)} chunks for processing", Fore.GREEN)
        
        # Create embeddings
        print_colored("Generating document embeddings...", Fore.YELLOW)
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            task_type="retrieval_document"
        )
        
        # Use Qdrant in-memory for vector storage
        vectorstore = Qdrant.from_documents(
            docs,
            embeddings,
            location=":memory:",
            collection_name="legal_case_documents"
        )
        
        # Create retriever with MMR for better diversity
        retriever = vectorstore.as_retriever(
            search_type="mmr",
            search_kwargs={
                "k": 5,
                "fetch_k": 10
            }
        )
        
        print_colored("✓ Vector database created successfully", Fore.GREEN)
        return retriever, docs
    
    except Exception as e:
        print_colored(f"Error processing PDF: {str(e)}", Fore.RED)
        return None, None

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

def format_response(response_text, style):
    """Format the response based on the determined style"""
    if SIMPLE_MODE:
        return f"{Fore.CYAN}Answer:{Style.RESET_ALL}\n\n{response_text}"
    
    if style == "summary":
        return f"{Fore.CYAN}📌 CASE SUMMARY:{Style.RESET_ALL}\n\n{response_text}"
    elif style == "list":
        return f"{Fore.CYAN}📋 KEY POINTS:{Style.RESET_ALL}\n\n{response_text}"
    elif style == "comparison":
        return f"{Fore.CYAN}⚖️ CASE COMPARISON:{Style.RESET_ALL}\n\n{response_text}"
    elif style == "explanation":
        return f"{Fore.CYAN}🔍 LEGAL EXPLANATION:{Style.RESET_ALL}\n\n{response_text}"
    elif style == "definition":
        return f"{Fore.CYAN}📖 LEGAL DEFINITION:{Style.RESET_ALL}\n\n{response_text}"
    elif style == "case_ruling":
        return f"{Fore.CYAN}⚡ PRECEDENT & RULING:{Style.RESET_ALL}\n\n{response_text}"
    elif style == "legal_reference":
        return f"{Fore.CYAN}📜 STATUTORY REFERENCE:{Style.RESET_ALL}\n\n{response_text}"
    elif style == "court_composition":
        return f"{Fore.CYAN}👨‍⚖️ COURT & JUDGES:{Style.RESET_ALL}\n\n{response_text}"
    else:
        return f"{Fore.CYAN}📄 LEGAL INFORMATION:{Style.RESET_ALL}\n\n{response_text}"

# Add a global variable to store conversation history
conversation_history = []

def save_history():
    with open(HISTORY_FILE, "wb") as f:
        pickle.dump(conversation_history, f)

def load_history():
    global conversation_history
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "rb") as f:
            conversation_history = pickle.load(f)

# Call load_history() at startup and save_history() on exit
load_history()

def get_llm_response(user_question, retriever):
    """Multi-agent response: Legal Assistant Agent + Search Agent fallback"""
    try:
        # 1. LEGAL ASSISTANT AGENT
        history_text = ""
        for i, (q, a) in enumerate(conversation_history):
            history_text += f"Previous Q{i+1}: {q}\nPrevious A{i+1}: {a}\n"

        response_style = determine_response_style(user_question)
        print_colored("Analyzing legal documents for your question...", Fore.YELLOW)

        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.3,
            max_output_tokens=2000,
            top_k=40,
            top_p=0.95
        )

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

        question_answer_chain = create_stuff_documents_chain(llm, prompt)
        rag_chain = create_retrieval_chain(retriever, question_answer_chain)

        response = rag_chain.invoke({"input": user_question})
        raw_answer = response["answer"]

        # Enhanced fallback detection for incomplete or vague answers
        fallback_phrases = [
            "i don't know", "not found", "unable to provide", "cannot find",
            "don't have access", "no information", "not available", "sorry",
            "as an ai", "i do not have", "i cannot", "i'm unable", "i am unable",
            "i do not possess", "i don't possess", "i don't have access"
        ]
        needs_fallback = (
            not raw_answer.strip() or
            any(phrase in raw_answer.lower() for phrase in fallback_phrases) or
            len(raw_answer.strip()) < 30  # Treat very short answers as incomplete
        )

        if needs_fallback:
            print_colored("Primary agent could not answer or answer is incomplete. Using Search Agent...", Fore.MAGENTA)
            search_answer = search_agent(user_question)
            if not search_answer or "no relevant information found" in search_answer.lower():
                final_answer = (
                    f"{Fore.YELLOW}Sorry, I could not find an answer in the documents or on the web for your question. "
                    f"Please try rephrasing or ask about another legal topic.{Style.RESET_ALL}"
                )
            else:
                final_answer = (
                    f"{Fore.YELLOW}Primary agent could not answer from documents or answer was incomplete.\n"
                    f"Here's what the Search Agent found:\n\n{search_answer}{Style.RESET_ALL}"
                )
        else:
            final_answer = format_response(raw_answer, response_style)

        # Store the Q&A in history
        conversation_history.append((user_question, final_answer))
        save_history()

        return final_answer

    except Exception as e:
        return f"{Fore.RED}⚠️ Error: {str(e)}. Please try again or rephrase your question.{Style.RESET_ALL}"


def search_agent(query):
    """
    A simple Search Agent that uses DuckDuckGo Instant Answer API.
    You can replace this with a more advanced web search or another LLM.
    """
    try:
        # DuckDuckGo Instant Answer API (no API key required)
        url = f"https://api.duckduckgo.com/?q={requests.utils.quote(query)}&format=json&no_redirect=1"
        resp = requests.get(url, timeout=5)
        data = resp.json()
        abstract = data.get("AbstractText")
        if abstract:
            return abstract
        related = data.get("RelatedTopics")
        if related and isinstance(related, list) and related[0].get("Text"):
            return related[0]["Text"]
        return "No relevant information found via web search."
    except Exception as e:
        return f"Search Agent error: {str(e)}"

def main():
    """Main application function"""
    print_header()
    
    # Check for PDF path from command line argument
    pdf_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_PDF_PATH
    
    # Process the PDF
    retriever, docs = process_pdf(pdf_path)
    
    if not retriever:
        print_colored("Failed to process the PDF. Please check the file path and try again.", Fore.RED)
        sys.exit(1)
    
    print_colored(f"\nSuccessfully processed legal case document!", Fore.GREEN, bold=True)
    print_colored(f"Contains {len(docs)} text segments for analysis\n", Fore.GREEN)
    
    print_colored("\nLEGAL CASE ASSISTANT READY", Fore.CYAN, bold=True)
    print_colored("Ask questions about cases, legal principles, or specific situations", Fore.CYAN)
    print_colored("Type 'exit' to quit the application\n", Fore.CYAN)
    
    # Main interaction loop
    while True:
        try:
            # Get user input
            user_question = input(f"{Fore.YELLOW}Your legal question:{Style.RESET_ALL} ")
            
            # Check for exit command
            if user_question.lower() in ['exit', 'quit', 'q']:
                print_colored("\nThank you for using the Legal Case Research Assistant.", Fore.CYAN)
                break
            
            # Check for simple mode toggle
            if user_question.lower() == 'simple':
                toggle_simple_mode()
                continue
            
            # Check for help command
            if user_question.lower() in ['help', '--help', '-h']:
                print_colored("Type your legal question and press Enter.", Fore.CYAN)
                print_colored("Type 'exit' to quit, 'simple' to toggle simple mode.", Fore.CYAN)
                continue
            
            # Skip empty questions
            if not user_question.strip():
                continue
            
            # Get and display response
            print("\n" + "-"*60)
            assistant_response = get_llm_response(user_question, retriever)
            print(assistant_response)
            print("-"*60 + "\n")
            
        except KeyboardInterrupt:
            print_colored("\n\nExiting Legal Case Research Assistant.", Fore.CYAN)
            break
        
        except Exception as e:
            print_colored(f"An error occurred: {str(e)}", Fore.RED)

def batch_mode(pdf_path, questions_file, output_file=None):
    """Run the assistant in batch mode with questions from a file"""
    global retriever
    
    print_header()
    print_colored(f"Running in batch mode with questions from: {questions_file}", Fore.CYAN)
    
    # Process the PDF
    retriever, doc_count = process_pdf(pdf_path)
    if not retriever:
        print_colored("Failed to process the PDF. Please check the file path and try again.", Fore.RED)
        sys.exit(1)
    
    # Read questions
    try:
        with open(questions_file, 'r') as f:
            questions = [line.strip() for line in f if line.strip()]
    except Exception as e:
        print_colored(f"Error reading questions file: {str(e)}", Fore.RED)
        sys.exit(1)
    
    # Prepare output
    results = []
    output = output_file or os.path.join(DATA_DIR, f"batch_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
    
    # Process each question
    for i, question in enumerate(questions):
        print_colored(f"\nProcessing question {i+1}/{len(questions)}: {question[:50]}{'...' if len(question) > 50 else ''}", Fore.YELLOW)
        
        try:
            # Get response without formatting
            query = LegalQuery(question)
            
            # Create LLM with Gemini model
            llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",
                temperature=0.2,
                max_output_tokens=2000,
                top_k=30,
                top_p=0.95
            )
            
            # Build prompt
            system_prompt = build_prompt_for_query_type(query)
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human", "{input}")
            ])
            
            # Create chains
            question_answer_chain = create_stuff_documents_chain(llm, prompt)
            rag_chain = create_retrieval_chain(retriever, question_answer_chain)
            
            # Get response
            response = rag_chain.invoke({"input": question})
            answer = response["answer"]
            
            # Add to results
            results.append({
                "question": question,
                "answer": answer,
                "query_type": query.query_type
            })
            
            print_colored("✓ Processed successfully", Fore.GREEN)
            
        except Exception as e:
            print_colored(f"Error processing question: {str(e)}", Fore.RED)
            results.append({
                "question": question,
                "answer": f"ERROR: {str(e)}",
                "query_type": "error"
            })
    
    # Write results to file
    try:
        with open(output, 'w') as f:
            f.write(f"LEGAL CASE RESEARCH RESULTS\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Document: {pdf_path}\n\n")
            
            for i, result in enumerate(results):
                f.write(f"QUESTION {i+1}: {result['question']}\n")
                f.write(f"TYPE: {result['query_type']}\n")
                f.write("-" * 50 + "\n")
                f.write(f"{result['answer']}\n\n")
                f.write("=" * 70 + "\n\n")
        
        print_colored(f"\nResults saved to: {output}", Fore.GREEN)
        
    except Exception as e:
        print_colored(f"Error saving results: {str(e)}", Fore.RED)

def toggle_simple_mode():
    global SIMPLE_MODE
    SIMPLE_MODE = not SIMPLE_MODE
    print_colored(f"Simple mode {'enabled' if SIMPLE_MODE else 'disabled'}", Fore.CYAN)

SIMPLE_MODE = False

def interactive_mode():
    """Interactive question-answering mode"""
    print_header()
    
    # Check for PDF path from command line argument
    pdf_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_PDF_PATH
    
    # Process the PDF
    retriever, docs = process_pdf(pdf_path)
    
    if not retriever:
        print_colored("Failed to process the PDF. Please check the file path and try again.", Fore.RED)
        sys.exit(1)
    
    print_colored(f"\nSuccessfully processed legal case document!", Fore.GREEN, bold=True)
    print_colored(f"Contains {len(docs)} text segments for analysis\n", Fore.GREEN)
    
    print_colored("\nLEGAL CASE ASSISTANT READY", Fore.CYAN, bold=True)
    print_colored("Ask questions about cases, legal principles, or specific situations", Fore.CYAN)
    print_colored("Type 'exit' to quit the application\n", Fore.CYAN)
    
    # Main interaction loop
    while True:
        try:
            # Get user input
            user_question = input(f"{Fore.YELLOW}Your legal question:{Style.RESET_ALL} ")
            
            # Check for exit command
            if user_question.lower() in ['exit', 'quit', 'q']:
                print_colored("\nThank you for using the Legal Case Research Assistant.", Fore.CYAN)
                break
            
            # Check for simple mode toggle
            if user_question.lower() == 'simple':
                toggle_simple_mode()
                continue
            
            # Check for help command
            if user_question.lower() in ['help', '--help', '-h']:
                print_colored("Type your legal question and press Enter.", Fore.CYAN)
                print_colored("Type 'exit' to quit, 'simple' to toggle simple mode.", Fore.CYAN)
                continue
            
            # Skip empty questions
            if not user_question.strip():
                continue
            
            # Get and display response
            print("\n" + "-"*60)
            assistant_response = get_llm_response(user_question, retriever)
            print(assistant_response)
            print("-"*60 + "\n")
            
        except KeyboardInterrupt:
            print_colored("\n\nExiting Legal Case Research Assistant.", Fore.CYAN)
            break
        
        except Exception as e:
            print_colored(f"An error occurred: {str(e)}", Fore.RED)

def export_case_database(output_file=None):
    """Export the extracted case information to a JSON file"""
    global case_info_cache
    
    if not case_info_cache:
        print_colored("No case information available to export.", Fore.YELLOW)
        return
    
    output = output_file or os.path.join(DATA_DIR, f"case_database_{datetime.now().strftime('%Y%m%d')}.json")
    
    try:
        with open(output, 'w') as f:
            json.dump({
                "generated_date": datetime.now().isoformat(),
                "case_count": len(case_info_cache),
                "cases": case_info_cache
            }, f, indent=2)
        
        print_colored(f"Case database exported to: {output}", Fore.GREEN)
    except Exception as e:
        print_colored(f"Error exporting case database: {str(e)}", Fore.RED)


def main():
    """Main application function"""
    # Check for command line arguments
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help']:
        print_colored("LEGAL CASE RESEARCH ASSISTANT", Fore.CYAN, bold=True)
        print("\nUsage:")
        print("  python legal_assistant.py [PDF_PATH]")
        print("  python legal_assistant.py [PDF_PATH] --batch [QUESTIONS_FILE] [OUTPUT_FILE]")
        print("\nOptions:")
        print("  PDF_PATH         Path to the PDF file containing legal cases")
        print("  --batch          Run in batch mode with questions from a file")
        print("  QUESTIONS_FILE   File containing one question per line")
        print("  OUTPUT_FILE      Optional file to save results (default: auto-generated)")
        print("  --export-cases   Export extracted case information to a JSON file")
        return
    
    # Get PDF path
    pdf_path = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith('-') else DEFAULT_PDF_PATH
    
    # Check for batch mode
    if "--batch" in sys.argv:
        batch_idx = sys.argv.index("--batch")
        questions_file = sys.argv[batch_idx + 1] if batch_idx + 1 < len(sys.argv) else None
        output_file = sys.argv[batch_idx + 2] if batch_idx + 2 < len(sys.argv) else None
        
        if not questions_file:
            print_colored("Error: Missing questions file for batch mode", Fore.RED)
            sys.exit(1)
        
        batch_mode(pdf_path, questions_file, output_file)
        return
    
    # Check for export cases option
    if "--export-cases" in sys.argv:
        export_idx = sys.argv.index("--export-cases")
        output_file = sys.argv[export_idx + 1] if export_idx + 1 < len(sys.argv) else None
        
        # First process the PDF to extract cases
        process_pdf(pdf_path)
        export_case_database(output_file)
        return
    
    # Default to interactive mode
    interactive_mode()


if __name__ == "__main__":
    main()

def toggle_simple_mode():
    global SIMPLE_MODE
    SIMPLE_MODE = not SIMPLE_MODE
    print_colored(f"Simple mode {'enabled' if SIMPLE_MODE else 'disabled'}", Fore.CYAN)