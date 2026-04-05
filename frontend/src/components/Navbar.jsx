import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Car, User, LogOut, Clock, LogIn } from 'lucide-react';

export default function Navbar({ user, onLogout, onLoginClick }) {
  const location = useLocation();
  const isActive = (path) => location.pathname === path;

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 glass-card rounded-none border-t-0 border-x-0 border-white/5">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <Link to="/" className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-tr from-blue-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg shadow-purple-500/20">
              <Car size={24} className="text-white" />
            </div>
            <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-400">
              DamageAI
            </span>
          </Link>

          <div className="flex items-center space-x-6">
            <Link 
              to="/" 
              className={`text-sm font-medium transition-colors ${isActive('/') ? 'text-white' : 'text-gray-400 hover:text-white'}`}
            >
              Scanner
            </Link>
            <Link 
              to="/history" 
              className={`text-sm font-medium transition-colors flex items-center space-x-1 ${isActive('/history') ? 'text-white' : 'text-gray-400 hover:text-white'}`}
            >
              <Clock size={16} />
              <span>History</span>
            </Link>
            
            <div className="h-6 w-px bg-white/10 mx-2"></div>
            
            {user ? (
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-2 text-sm text-gray-300">
                  <div className="w-8 h-8 rounded-full bg-white/5 flex items-center justify-center border border-white/10">
                    <User size={16} className="text-gray-400" />
                  </div>
                  <span>{user.username}</span>
                </div>
                <button 
                  onClick={onLogout}
                  className="text-gray-400 hover:text-red-400 transition-colors p-2 rounded-lg hover:bg-red-500/10"
                  title="Logout"
                >
                  <LogOut size={18} />
                </button>
              </div>
            ) : (
              <button 
                onClick={onLoginClick}
                className="gradient-btn py-2 px-4 shadow-none text-sm flex items-center space-x-2 rounded-lg"
              >
                <LogIn size={16} /> <span>Login</span>
              </button>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}
