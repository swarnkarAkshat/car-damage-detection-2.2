import React, { useState, useRef, useEffect } from 'react';
import { Bot, X, Send, Loader2 } from 'lucide-react';
import { api } from '../api/client';

export default function ChatWidget({ user, openAuthModal, scanResult, explanation }) {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    { role: 'bot', text: 'Hello! I am your AI assistant. How can I help you regarding your car scan or general maintenance today?' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isOpen]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;
    
    if (!user) {
      setMessages(prev => [...prev, { role: 'bot', text: 'Please log in to use the chat feature!' }]);
      setInput('');
      setTimeout(() => openAuthModal(), 1500);
      return;
    }

    const msg = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', text: msg }]);
    setLoading(true);
    
    try {
      const context = scanResult ? `Prediction: ${scanResult.prediction}, Confidence: ${scanResult.confidence}%, Explanation: ${explanation || 'None'}` : null;
      const res = await api.chat(msg, context);
      setMessages(prev => [...prev, { role: 'bot', text: res.reply }]);
    } catch (err) {
      setMessages(prev => [...prev, { role: 'bot', text: 'Unable to reach the server. Please try again later.' }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <button 
        onClick={() => setIsOpen(!isOpen)}
        className={`fixed bottom-6 right-6 w-16 h-16 bg-linear-to-tr from-[#4F46E5] to-[#9333EA] rounded-full flex items-center justify-center text-white shadow-[0_0_20px_rgba(79,70,229,0.5)] transition-all duration-500 z-60 group hover:scale-110 active:scale-95`}
      >
        <div className={`absolute inset-0 rounded-full bg-linear-to-tr from-[#4F46E5] to-[#9333EA] animate-ping opacity-20 group-hover:opacity-40 transition-opacity ${isOpen ? 'hidden' : 'block'}`}></div>
        <div className="relative transition-transform duration-500 rotate-0">
          {isOpen ? <X size={32} className="animate-in fade-in zoom-in duration-300" /> : <Bot size={32} className="animate-in fade-in zoom-in duration-300" />}
        </div>
      </button>

      {/* Chat window */}
      <div className={`fixed bottom-24 right-6 w-96 max-w-[calc(100vw-32px)] h-[550px] max-h-[calc(100vh-120px)] glass-card flex flex-col z-50 transition-all origin-bottom-right ${isOpen ? 'scale-100 opacity-100 translate-y-0' : 'scale-0 opacity-0 translate-y-10 pointer-events-none'}`}>
        <div className="flex items-center justify-between p-4 border-b border-white/10 bg-white/5 rounded-t-2xl">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 rounded-full bg-linear-to-tr from-[#6366F1] to-[#D946EF] flex items-center justify-center">
              <Bot size={16} className="text-white" />
            </div>
            <span className="font-semibold text-white">AI Assistant</span>
          </div>
          <button onClick={() => setIsOpen(false)} className="text-gray-400 hover:text-white transition-colors">
            <X size={20} />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((msg, idx) => (
            <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[80%] rounded-2xl p-3 text-sm ${
                msg.role === 'user' 
                  ? 'bg-blue-600 text-white rounded-tr-sm' 
                  : 'bg-white/10 text-gray-200 border border-white/5 rounded-tl-sm'
              }`}>
                {msg.text}
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex justify-start">
               <div className="max-w-[80%] rounded-2xl p-3 bg-white/10 text-gray-400 border border-white/5 rounded-tl-sm flex items-center space-x-2">
                 <Loader2 size={16} className="animate-spin" />
                 <span className="text-sm">Thinking...</span>
               </div>
            </div>
          )}
          <div ref={endRef} />
        </div>

        <div className="p-4 border-t border-white/10 bg-white/5 rounded-b-2xl">
          <form 
            onSubmit={(e) => { e.preventDefault(); handleSend(); }}
            className="flex items-center space-x-2 relative"
          >
            <input 
              type="text" 
              placeholder="Ask anything..." 
              value={input}
              onChange={e => setInput(e.target.value)}
              className="glass-input pr-12 w-full text-sm"
            />
            <button 
              type="submit" 
              disabled={loading || !input.trim()}
              className="absolute right-1 w-10 h-10 rounded-xl bg-blue-500 hover:bg-blue-600 flex items-center justify-center transition-colors disabled:opacity-50"
            >
              <Send size={16} className="text-white" />
            </button>
          </form>
        </div>
      </div>
    </>
  );
}
