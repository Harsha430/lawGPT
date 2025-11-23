import React from 'react';
import { Outlet } from 'react-router-dom';
import Navbar from '../components/Navbar';
import './MainLayout.css';

const MainLayout = () => {
  return (
    <div className="main-layout">
      <div className="animated-background">
        <div className="gradient-orb orb-1"></div>
        <div className="gradient-orb orb-2"></div>
        <div className="gradient-orb orb-3"></div>
      </div>
      
      <Navbar />
      
      <main className="main-content">
        <Outlet />
      </main>
    </div>
  );
};

export default MainLayout;
