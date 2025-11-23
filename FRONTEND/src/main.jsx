import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import './index.css';
import MainLayout from './layouts/MainLayout';
import ChatPage from './pages/ChatPage';
import BasicRightsPage from './pages/BasicRightsPage';

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<MainLayout />}>
          <Route index element={<ChatPage />} />
          <Route path="basic-rights" element={<BasicRightsPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  </StrictMode>,
);
