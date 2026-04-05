import React, { useEffect, useState } from 'react';
import { Download, Trash2, Lock, Loader2, ArrowLeft } from 'lucide-react';
import { Link } from 'react-router-dom';
import { api } from '../api/client';

export default function History({ user, openAuthModal }) {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (user) {
      fetchHistory();
    } else {
      setLoading(false);
    }
  }, [user]);

  const fetchHistory = async () => {
    try {
      const data = await api.getHistory();
      // Sort: newest first
      setHistory(data.sort((a, b) => b.id - a.id));
    } catch (err) {
      setError("Failed to load history.");
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Delete this record?")) return;
    try {
      await api.deleteHistory(id);
      setHistory(prev => prev.filter(r => r.id !== id));
    } catch (err) {
      alert("Failed to delete record");
    }
  };

  const handleDownloadPDF = async (item) => {
    try {
      // Use the stored explanation and image_data for a complete professional report
      const url = await api.generateReportUrl(
        item.prediction,
        item.confidence,
        item.explanation || "No description saved.",
        item.image_data,
        item.cost,
        item.damage_percentage
      );
      const link = document.createElement('a');
      link.href = url;
      link.download = `Damage_Report_${item.id}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (err) {
      alert("Failed to generate PDF document.");
    }
  };

  const formatPrediction = (raw) => {
    if (!raw) return 'Unknown';
    return raw.replace('F_', 'Front ').replace('R_', 'Rear ').replace('_', ' ');
  };

  if (loading) return (
    <div className="min-h-screen bg-[#0B1120] text-white flex flex-col items-center justify-center">
      <Loader2 className="animate-spin text-blue-500 mb-4" size={48} />
      <p className="text-gray-400">Loading your history...</p>
    </div>
  );

  return (
    <div className="py-8 px-4 max-w-6xl mx-auto">

      {!user ? (
        <div className="glass-card p-12 flex flex-col items-center justify-center text-center mt-12 bg-white/5 backdrop-blur-xl border border-white/10 rounded-3xl">
          <div className="w-20 h-20 bg-blue-500/10 rounded-full flex items-center justify-center mb-6">
            <Lock size={36} className="text-blue-400" />
          </div>
          <h2 className="text-2xl font-bold mb-3 text-white">Access Denied</h2>
          <p className="text-gray-400 mb-8 max-w-md text-lg">Please sign in to view your scan history and download professional reports.</p>
          <button onClick={openAuthModal} className="gradient-btn px-10 py-3 text-lg font-semibold rounded-xl">Sign In Now</button>
        </div>
      ) : (
        <>
          <div className="flex flex-col sm:flex-row items-center justify-between mb-10 gap-6">
            <div>
              <Link to="/" className="flex items-center text-gray-400 hover:text-white transition-colors mb-4 group text-sm">
                <ArrowLeft size={16} className="mr-2 transform group-hover:-translate-x-1 transition-transform" /> Back
              </Link>
              <h1 className="text-4xl font-extrabold text-white tracking-tight">Prediction History</h1>
            </div>
            {history.length > 0 && (
              <div className="bg-white/5 px-4 py-2 rounded-xl border border-white/5 text-sm text-gray-400">
                Found <span className="text-blue-400 font-bold">{history.length}</span> scan records
              </div>
            )}
          </div>

          {error && (
            <div className="mb-6 p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400">
              {error}
            </div>
          )}

          <div className="glass-card overflow-hidden border border-white/10 rounded-3xl bg-[#0F172A]/50 backdrop-blur-2xl shadow-2xl">
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="bg-white/5 border-b border-white/10">
                    <th className="py-6 px-6 text-xs font-black text-gray-400 uppercase tracking-widest">#</th>
                    <th className="py-6 px-6 text-xs font-black text-gray-400 uppercase tracking-widest">Result</th>
                    <th className="py-6 px-6 text-xs font-black text-gray-400 uppercase tracking-widest text-center">Damage %</th>
                    <th className="py-6 px-6 text-xs font-black text-gray-400 uppercase tracking-widest text-center">Cost</th>
                    <th className="py-6 px-6 text-xs font-black text-gray-400 uppercase tracking-widest text-center">Report</th>
                    <th className="py-6 px-6 text-xs font-black text-gray-400 uppercase tracking-widest text-center">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5">
                  {history.map((record) => {
                    const predText = formatPrediction(record.prediction);
                    return (
                      <tr key={record.id} className="hover:bg-white/[0.03] transition-all group">
                        <td className="py-6 px-6">
                          <span className="text-gray-500 font-mono text-sm">#{record.id}</span>
                        </td>
                        <td className="py-6 px-6">
                          <div className="flex items-center space-x-3">
                            <div className={`w-2.5 h-2.5 rounded-full shadow-[0_0_8px_rgba(0,0,0,0.5)] ${
                              record.prediction?.toLowerCase().includes('normal') 
                              ? 'bg-green-500 shadow-green-500/50' 
                              : 'bg-red-500 shadow-red-500/50'
                            }`}></div>
                            <span className="font-bold text-white text-base lg:text-lg">{predText}</span>
                          </div>
                        </td>
                        <td className="py-6 px-6 text-center">
                          <span className="text-blue-400 font-black text-lg">{record.damage_percentage}%</span>
                        </td>
                        <td className="py-6 px-6 text-center">
                          <span className="text-blue-400 font-black text-lg">INR {(record.cost || 0).toLocaleString()}</span>
                        </td>
                        <td className="py-6 px-6 text-center">
                          <button
                            onClick={() => handleDownloadPDF(record)}
                            className="bg-white/5 border border-white/10 text-gray-300 hover:text-white hover:bg-white/10 hover:border-white/20 px-5 py-2.5 rounded-xl transition-all flex items-center space-x-2 mx-auto text-sm font-bold"
                          >
                            <Download size={16} />
                            <span>PDF</span>
                          </button>
                        </td>
                        <td className="py-6 px-6 text-center">
                          <button
                            onClick={() => handleDelete(record.id)}
                            className="w-10 h-10 rounded-xl bg-red-500/10 text-red-500/50 hover:text-red-500 hover:bg-red-500/20 transition-all flex items-center justify-center mx-auto"
                            title="Delete Record"
                          >
                            <Trash2 size={18} />
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                  {history.length === 0 && (
                    <tr>
                      <td colSpan="6" className="py-20 text-center">
                        <div className="flex flex-col items-center grayscale opacity-50">
                          <Loader2 size={48} className="text-gray-600 mb-4 animate-pulse" />
                          <p className="text-gray-500 text-lg">Your scan history is empty.</p>
                          <Link to="/" className="text-blue-400 hover:text-blue-300 mt-2 text-sm">Start your first scan</Link>
                        </div>
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
