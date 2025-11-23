import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FaPaperPlane, FaUserAlt, FaRobot, FaPlus, FaLightbulb } from 'react-icons/fa';
import { BounceLoader } from 'react-spinners';
import './ChatPage.css';

const ChatPage = () => {
  const [question, setQuestion] = useState('');
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const chatEndRef = useRef(null);
  const inputRef = useRef(null);

  const suggestedQuestions = [
    {
      icon: "⚖️",
      question: "What are my fundamental rights as an Indian citizen?",
      category: "Constitutional Law"
    },
    {
      icon: "📋",
      question: "Explain the procedure for filing a consumer complaint",
      category: "Consumer Law"
    },
    {
      icon: "🏠",
      question: "What are the tenant rights under the Rent Control Act?",
      category: "Property Law"
    },
    {
      icon: "💼",
      question: "What is the notice period required for resignation in India?",
      category: "Labor Law"
    }
  ];

  useEffect(() => {
    if (chatEndRef.current) {
      chatEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [history]);

  useEffect(() => {
    if (inputRef.current && history.length === 0) {
      inputRef.current.focus();
    }
  }, [history]);

  const handleAsk = async (questionText) => {
    const queryText = questionText || question;
    if (!queryText.trim()) return;
    
    const tempId = Date.now();
    setHistory([...history, { id: tempId, question: queryText, answer: null, loading: true }]);
    setLoading(true);
    setQuestion('');

    try {
      const response = await fetch('http://127.0.0.1:8800/api/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: queryText }),
      });

      if (!response.ok) {
        throw new Error('Server error. Please try again.');
      }

      const data = await response.json();
      
      setHistory(prevHistory => 
        prevHistory.map(item => 
          item.id === tempId 
            ? { ...item, answer: data.answer, loading: false } 
            : item
        )
      );
    } catch (err) {
      setHistory(prevHistory => 
        prevHistory.map(item => 
          item.id === tempId 
            ? { ...item, answer: "Sorry, I couldn't get a response. Please check if the backend server is running.", loading: false, isError: true } 
            : item
        )
      );
    } finally {
      setLoading(false);
    }
  };

  const handleSuggestedQuestion = (suggestedQ) => {
    handleAsk(suggestedQ);
  };

  const handleNewChat = () => {
    setHistory([]);
    setQuestion('');
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    handleAsk();
  };

  return (
    <div className="chat-page-redesign">
      <div className="chat-wrapper">
        {/* Messages Container */}
        <div className="messages-area">
          {history.length === 0 ? (
            <motion.div
              className="welcome-section"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
            >
              <motion.h1 
                className="welcome-title"
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
              >
                How can I help you with legal matters today?
              </motion.h1>
              
              <motion.div 
                className="suggestions-grid"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.4 }}
              >
                {suggestedQuestions.map((item, idx) => (
                  <motion.button
                    key={idx}
                    className="suggestion-card"
                    onClick={() => handleSuggestedQuestion(item.question)}
                    whileHover={{ scale: 1.02, y: -2 }}
                    whileTap={{ scale: 0.98 }}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.5 + idx * 0.1 }}
                  >
                    <div className="suggestion-icon">{item.icon}</div>
                    <div className="suggestion-content">
                      <span className="suggestion-category">{item.category}</span>
                      <p className="suggestion-text">{item.question}</p>
                    </div>
                  </motion.button>
                ))}
              </motion.div>
            </motion.div>
          ) : (
            <div className="chat-messages">
              <AnimatePresence>
                {history.map((item, idx) => (
                  <motion.div
                    key={item.id || idx}
                    className="message-pair"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3 }}
                  >
                    {/* User Message */}
                    <div className="message user-message">
                      <div className="message-content">
                        <div className="avatar user-avatar">
                          <FaUserAlt />
                        </div>
                        <div className="message-text">
                          <div className="message-label">You</div>
                          <p>{item.question}</p>
                        </div>
                      </div>
                    </div>

                    {/* Assistant Message */}
                    <div className="message assistant-message">
                      <div className="message-content">
                        <div className="avatar assistant-avatar">
                          <FaRobot />
                        </div>
                        <div className="message-text">
                          <div className="message-label">LawGPT Assistant</div>
                          {item.loading ? (
                            <div className="loading-indicator">
                              <BounceLoader color="#2563eb" size={20} />
                              <span>Analyzing legal information...</span>
                            </div>
                          ) : (
                            <p className={item.isError ? 'error-text' : ''}>{item.answer}</p>
                          )}
                        </div>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>
              <div ref={chatEndRef} />
            </div>
          )}
        </div>

        {/* Input Area - Fixed at bottom */}
        <div className="input-section">
          <div className="input-container-new">
            {history.length > 0 && (
              <motion.button
                className="new-chat-btn"
                onClick={handleNewChat}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                title="New Chat"
              >
                <FaPlus />
              </motion.button>
            )}
            
            <form onSubmit={handleSubmit} className="input-form">
              <input
                ref={inputRef}
                type="text"
                value={question}
                onChange={e => setQuestion(e.target.value)}
                placeholder="Ask a legal question..."
                disabled={loading}
                className="chat-input"
              />
              
              <motion.button
                type="submit"
                disabled={loading || !question.trim()}
                className="send-btn"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                {loading ? (
                  <BounceLoader color="#fff" size={16} />
                ) : (
                  <FaPaperPlane />
                )}
              </motion.button>
            </form>
          </div>
          
          <p className="disclaimer-text">
            LawGPT can make mistakes. Verify important legal information with a qualified attorney.
          </p>
        </div>
      </div>
    </div>
  );
};

export default ChatPage;
