import React, { useState } from 'react';
import { User, Lock, Mail, X, Car } from 'lucide-react';
import { api } from '../api/client';

export default function AuthModal({ onClose, onAuthSuccess }) {
  const [isRegistering, setIsRegistering] = useState(false);
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      if (isRegistering) {
        await api.register(username, email, password);
      }
      await api.login(username, password);
      const user = await api.getCurrentUser();
      if(user) {
        onAuthSuccess(user);
        onClose();
      }
    } catch (err) {
      setError(err.message || (isRegistering ? "Registration failed. Details may be taken." : "Invalid credentials."));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm px-4">
      <div className="glass-card w-full max-w-md p-8 relative animate-in fade-in zoom-in duration-200">
        
        <button 
          onClick={onClose} 
          className="absolute top-4 right-4 text-gray-400 hover:text-white transition-colors p-1"
        >
          <X size={24} />
        </button>

        <div className="mb-6 flex flex-col items-center">
          <div className="w-12 h-12 bg-gradient-to-tr from-blue-500 to-purple-600 rounded-xl flex items-center justify-center mb-3 shadow-lg shadow-purple-500/20">
            <Car size={24} className="text-white" />
          </div>
          <h2 className="text-2xl font-bold">{isRegistering ? "Create Account" : "Welcome Back"}</h2>
        </div>

        {error && <div className="bg-red-500/10 border border-red-500/50 text-red-400 px-4 py-3 rounded-xl mb-6 text-sm text-center">{error}</div>}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="relative">
            <User className="absolute left-4 top-3.5 text-gray-400" size={20} />
            <input 
              type="text" 
              placeholder={isRegistering ? "Choose a Username" : "Username or Email"} 
              className="glass-input pl-12"
              value={username} onChange={e => setUsername(e.target.value)} required
            />
          </div>
          
          {isRegistering && (
            <div className="relative">
              <Mail className="absolute left-4 top-3.5 text-gray-400" size={20} />
              <input 
                type="email" 
                placeholder="Email Address" 
                className="glass-input pl-12"
                value={email} onChange={e => setEmail(e.target.value)} required
              />
            </div>
          )}

          <div className="relative">
            <Lock className="absolute left-4 top-3.5 text-gray-400" size={20} />
            <input 
              type="password" 
              placeholder="Password" 
              className="glass-input pl-12"
              value={password} onChange={e => setPassword(e.target.value)} required
            />
          </div>

          <button type="submit" disabled={loading} className="gradient-btn w-full mt-2 py-3.5">
            {loading ? 'Authenticating...' : (isRegistering ? 'Sign Up' : 'Sign In')}
          </button>
        </form>

        <p className="mt-6 text-center text-gray-400 text-sm">
          {isRegistering ? "Already have an account?" : "Don't have an account?"}&nbsp;
          <button 
            type="button" 
            onClick={() => { setIsRegistering(!isRegistering); setError(null); }} 
            className="text-blue-400 hover:text-blue-300 font-medium transition-colors"
          >
            {isRegistering ? "Sign in instead" : "Register here"}
          </button>
        </p>

      </div>
    </div>
  );
}
