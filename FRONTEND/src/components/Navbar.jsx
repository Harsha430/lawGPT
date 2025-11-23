import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { FaBalanceScale, FaComments, FaScroll } from 'react-icons/fa';
import './Navbar.css';

const Navbar = () => {
  const location = useLocation();

  return (
    <motion.nav 
      className="navbar"
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ type: "spring", stiffness: 100 }}
    >
      <div className="navbar-container">
        <Link to="/" className="logo-container">
          <motion.div
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="logo-content"
          >
            <FaBalanceScale className="logo-icon" />
            <div className="logo-text-group">
              <span className="logo-text text-gradient">LawGPT</span>
              <span className="logo-subtitle">Legal Research Assistant</span>
            </div>
          </motion.div>
        </Link>

        <div className="nav-links">
          <Link to="/" className={location.pathname === '/' ? 'active' : ''}>
            <motion.div
              whileHover={{ scale: 1.05, y: -2 }}
              whileTap={{ scale: 0.95 }}
              className="nav-link"
            >
              <FaComments />
              <span>Chat</span>
            </motion.div>
          </Link>
          
          <Link to="/basic-rights" className={location.pathname === '/basic-rights' ? 'active' : ''}>
            <motion.div
              whileHover={{ scale: 1.05, y: -2 }}
              whileTap={{ scale: 0.95 }}
              className="nav-link"
            >
              <FaScroll />
              <span>Basic Rights</span>
            </motion.div>
          </Link>
        </div>
      </div>
    </motion.nav>
  );
};

export default Navbar;
