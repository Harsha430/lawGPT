# Legal Research Assistant

An intelligent legal research system that combines PDF document analysis and web search capabilities to provide comprehensive legal information and answers.

## 🌟 Features

- **Dual-Agent System**

  - PDF-based analysis for local legal documents
  - Web search integration for current legal information
  - Intelligent fallback mechanism for comprehensive answers

- **Modern User Interface**

  - Clean, responsive React frontend
  - Real-time chat interface
  - Helpful sidebar with legal tips
  - Professional gradient styling

- **Smart Document Processing**
  - PDF document analysis
  - Context-aware responses
  - Conversation history management

## 🔧 Technology Stack

### Frontend

- React with Vite
- Modern CSS with animations
- Responsive design principles

### Backend

- Python FastAPI server
- PDF processing capabilities
- DuckDuckGo integration for web search
- Conversation state management

## 📋 Prerequisites

- Python 3.10 or higher
- Node.js 14.0 or higher
- npm or yarn package manager

## 🚀 Getting Started

1. **Clone the repository**

   ```powershell
   git clone [repository-url]
   cd law
   ```

2. **Set up the Backend**

   ```powershell
   cd BACKEND
   python -m venv env_py10
   .\env_py10\Scripts\Activate
   pip install -r requirements.txt
   ```

3. **Set up the Frontend**

   ```powershell
   cd FROUNTEND
   npm install
   ```

4. **Start the Development Servers**

   Backend:

   ```powershell
   cd BACKEND
   .\env_py10\Scripts\Activate
   python api_server.py
   ```

   Frontend:

   ```powershell
   cd FROUNTEND
   npm run dev
   ```

5. **Access the Application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000

## 📁 Project Structure

```
├── BACKEND/
│   ├── api_server.py    # FastAPI server implementation
│   ├── law.py          # Core legal processing logic
│   ├── requirements.txt # Python dependencies
│   └── main.py         # Application entry point
├── FROUNTEND/
│   ├── src/
│   │   ├── App.jsx     # Main React component
│   │   └── App.css     # Styles
│   ├── package.json    # Node.js dependencies
│   └── vite.config.js  # Vite configuration
└── books/              # Directory for legal document PDFs
```

## ⚙️ Configuration

1. Place your legal PDF documents in the `books/` directory
2. Environment variables can be set in `.env` file:
   ```
   PORT=8000
   ```

## 🔐 Security

- PDF files and conversation history are excluded from version control
- Proper error handling for malformed requests
- Secure API endpoints

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Thanks to all contributors
- Built with React + Vite
- Powered by Python FastAPI
