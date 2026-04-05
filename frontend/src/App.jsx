import React, { useEffect, useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { api } from './api/client';

import Home from './pages/Home';
import History from './pages/History';
import Navbar from './components/Navbar';
import ChatWidget from './components/ChatWidget';
import AuthModal from './components/AuthModal';

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [currentResult, setCurrentResult] = useState(null);
  const [currentExplanation, setCurrentExplanation] = useState(null);

  useEffect(() => {
    api.getCurrentUser().then(userData => {
      setUser(userData);
      setLoading(false);
    }).catch(() => {
      setUser(null);
      setLoading(false);
    });
  }, []);

  const handleLogout = () => {
    api.logout();
    setUser(null);
  };

  if (loading) return <div className="min-h-screen bg-[#0B1120] text-white flex items-center justify-center">Loading...</div>;

  return (
    <BrowserRouter>
      <Navbar user={user} onLogout={handleLogout} onLoginClick={() => setShowAuthModal(true)} />
      
      <div className="pt-20 px-4 max-w-7xl mx-auto relative min-h-screen pb-20">
        <Routes>
          <Route path="/" element={
            <Home 
              user={user} 
              openAuthModal={() => setShowAuthModal(true)} 
              setGlobalResult={setCurrentResult}
              setGlobalExplanation={setCurrentExplanation}
            />
          } />
          <Route path="/history" element={<History user={user} openAuthModal={() => setShowAuthModal(true)} />} />
        </Routes>
      </div>
      
      <ChatWidget 
        user={user} 
        openAuthModal={() => setShowAuthModal(true)} 
        scanResult={currentResult}
        explanation={currentExplanation}
      />

      {showAuthModal && (
        <AuthModal 
          onClose={() => setShowAuthModal(false)}
          onAuthSuccess={(userData) => setUser(userData)}
        />
      )}
    </BrowserRouter>
  );
}

export default App;
