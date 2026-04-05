import React from 'react';
import { Download, AlertCircle } from 'lucide-react';
import { getDamageDetails, cleanAIExplanation } from '../utils/costCalculator';

export default function ResultCard({ result, explanation, onDownloadPDF }) {
  if (!result) {
    return (
      <div className="glass-card p-6 h-full flex flex-col items-center justify-center text-center text-gray-400 min-h-[400px]">
        <AlertCircle size={48} className="mb-4 text-white/20" />
        <p>Results and AI explanation will appear here after analysis.</p>
      </div>
    );
  }

  const confPercentage = (result.confidence * 100).toFixed(1);
  
  const formatPrediction = (raw) => {
    return raw.replace('F_', 'Front ').replace('R_', 'Rear ').replace('_', ' ');
  };

  const predictionText = formatPrediction(result.prediction);
  const details = getDamageDetails(predictionText);

  return (
    <div className="glass-card p-8 h-full flex flex-col items-center text-center">
      
      <p className="text-sm uppercase tracking-[0.2em] font-bold text-gray-400 mb-2 mt-4">
        Detection Result
      </p>
      <div className="flex items-center space-x-3 mb-8">
        <div className={`w-3 h-3 rounded-full shadow-[0_0_12px_rgba(0,0,0,0.5)] ${
          result.prediction?.toLowerCase().includes('normal') 
          ? 'bg-green-500 shadow-green-500/50' 
          : 'bg-red-500 shadow-red-500/50'
        }`}></div>
        <h2 className="text-4xl font-bold text-white uppercase">{predictionText}</h2>
      </div>

      <div className="w-full bg-[#4B4C5C]/80 rounded-xl py-6 px-4 mb-4 flex flex-col shadow-inner">
        <p className="text-xl font-bold text-white mb-2">
          Damage: <span className="font-normal">{details.damage}%</span>
        </p>
        <p className="text-xl font-bold text-yellow-400">
          Est. Cost: <span className="font-normal">INR {details.cost.toLocaleString()}</span>
        </p>
      </div>

      <div className="w-full h-8 bg-[#252636] rounded-full flex items-center justify-start mb-8 relative overflow-hidden ring-1 ring-white/10 shadow-inner">
         <div 
           className="h-full bg-linear-to-r from-emerald-500 to-green-500 flex items-center justify-center transition-all duration-1000 ease-out shadow-[0_0_15px_rgba(16,185,129,0.4)]"
           style={{ width: `${confPercentage}%` }}
         >
           <span className="text-white text-xs font-black uppercase tracking-widest whitespace-nowrap px-4 drop-shadow-md">
             {confPercentage}% Confidence
           </span>
         </div>
      </div>

      <div className="w-full flex-1 text-left bg-[#252636]/60 rounded-xl p-6 border border-white/5 shadow-inner">
        <h3 className="text-lg font-bold text-cyan-400 uppercase tracking-widest mb-4">
          AI Explanation
        </h3>
        <div className="text-gray-200 text-sm leading-relaxed prose prose-invert">
          {explanation ? (
             <p className="whitespace-pre-wrap">{cleanAIExplanation(explanation)}</p>
          ) : (
             <span className="animate-pulse">Generating AI expert explanation...</span>
          )}
        </div>
      </div>

      {explanation && (
        <button 
          onClick={onDownloadPDF}
          className="mt-6 w-full bg-blue-600 hover:bg-blue-500 text-white font-semibold py-4 rounded-xl transition-all shadow-lg"
        >
          Download PDF Report
        </button>
      )}
    </div>
  );
}
