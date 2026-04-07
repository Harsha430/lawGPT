# LawGPT ⚖️

LawGPT is an AI-powered Legal Research Assistant designed to help navigate and understand legal documents using Retrieval-Augmented Generation (RAG). It specifically focuses on answering queries based on the new Indian legal codes:
- **BNS** (Bharatiya Nyaya Sanhita)
- **BNSS** (Bharatiya Nagarik Suraksha Sanhita)
- **BSA** (Bharatiya Sakshya Adhiniyam)

## Table of Contents
- [Architecture](#architecture)
- [Technologies Used](#technologies-used)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
- [Environment Variables](#environment-variables)
- [Running the Application](#running-the-application)

---

## Architecture

LawGPT uses a modern backend driven by **FastAPI** to handle user queries. It fetches contextually relevant legal sections using **Pinecone Vector Database** and **Hugging Face Sentence Transformers**. The retrieval is then augmented and sent to **Google Gen AI (Gemini)** to generate accurate, context-aware legal advice. A dynamic **React** frontend provides a sleek and interactive UI.

## Technologies Used

### Frontend
- **React.js** (Vite)
- **Material-UI (MUI)**
- **Framer Motion** (Animations)
- **React Router**

### Backend
- **FastAPI** (Python web framework)
- **Pinecone** (Vector Database)
- **LangChain** (Framework for LLMs)
- **Google Gen AI** (Gemini LLM for answers)
- **Sentence Transformers** (`all-MiniLM-L6-v2` for embeddings)
- **PyPDF / PDFPlumber** (Document ingestion)

## Project Structure

```text
lawGPT-main/
├── BACKEND/
│   ├── books/                  # Contains the legal PDF documents
│   ├── bot.py                  # FastAPI server and endpoints
│   ├── build_db.py             # Script to ingest PDFs, generate embeddings, and populate Pinecone
│   ├── system_prompt.txt       # Core prompt for the Gen AI model
│   ├── requirements.txt        # Python dependencies
│   └── ...
├── FRONTEND/
│   ├── src/                    # React components and views
│   ├── package.json            # Node.js dependencies
│   ├── vite.config.js          # Vite configuration
│   └── ...
└── README.md
```

## Getting Started

### Prerequisites
- Node.js (v16+)
- Python 3.9+
- A Pinecone account and API key
- Google Gemini API key

### Environment Variables
You need to create a `.env` file in the `BACKEND` directory with the following variables:
```env
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX_NAME=lawgpt
GOOGLE_API_KEY=your_google_gen_ai_key
```

### Backend Setup
1. Navigate to the `BACKEND` directory.
   ```bash
   cd BACKEND
   ```
2. Create and activate a Python virtual environment.
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```
3. Install the dependencies.
   ```bash
   pip install -r requirements.txt
   ```
4. Build the vector database (Requires your PDFs in the `books/` folder).
   ```bash
   python build_db.py
   ```

### Frontend Setup
1. Navigate to the `FRONTEND` directory.
   ```bash
   cd FRONTEND
   ```
2. Install Node dependencies.
   ```bash
   npm install
   ```

## Running the Application

1. **Start the Backend Server**:
   ```bash
   cd BACKEND
   # Ensure your virtual environment is active
   uvicorn bot:app --reload
   ```

2. **Start the Frontend Client**:
   ```bash
   cd FRONTEND
   npm run dev
   ```

3. Open your browser and go to `http://localhost:5173` (or the port specified by Vite) to interact with LawGPT!
