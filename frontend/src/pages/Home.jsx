import React, { useState } from 'react';
import UploadCard from '../components/UploadCard';
import ResultCard from '../components/ResultCard';
import { api } from '../api/client';
import { getDamageDetails } from '../utils/costCalculator';

export default function Home({ user, openAuthModal, setGlobalResult, setGlobalExplanation }) {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [explanation, setExplanation] = useState(null);
  const [error, setError] = useState(null);
  const [currentFile, setCurrentFile] = useState(null);

  const formatPrediction = (raw) => {
    if (!raw) return '';
    return raw.replace('F_', 'Front ').replace('R_', 'Rear ').replace('_', ' ');
  };

  const handleAnalyze = async (file) => {
    if (!user) {
      openAuthModal();
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);
    setExplanation(null);
    setGlobalResult(null);
    setGlobalExplanation(null);
    setCurrentFile(file);

    try {
      // 1. Predict
      const predRes = await api.predict(file);
      setResult(predRes);
      setGlobalResult(predRes);

      // 2. Fetch AI Explanation
      const expRes = await api.explain(predRes.prediction, predRes.confidence);
      setExplanation(expRes.explanation);
      setGlobalExplanation(expRes.explanation);

      // 3. Save to History with full context
      try {
        const details = getDamageDetails(formatPrediction(predRes.prediction));
        
        const fileToOptimizedBase64 = (file) => new Promise((resolve, reject) => {
          const reader = new FileReader();
          reader.readAsDataURL(file);
          reader.onload = (event) => {
            const img = new Image();
            img.src = event.target.result;
            img.onload = () => {
              const canvas = document.createElement('canvas');
              const MAX_WIDTH = 512;
              let width = img.width;
              let height = img.height;
              if (width > MAX_WIDTH) { height *= MAX_WIDTH / width; width = MAX_WIDTH; }
              canvas.width = width; canvas.height = height;
              const ctx = canvas.getContext('2d');
              ctx.drawImage(img, 0, 0, width, height);
              resolve(canvas.toDataURL('image/jpeg', 0.6));
            };
          };
          reader.onerror = error => reject(error);
        });

        const historyImage = await fileToOptimizedBase64(file);
        await api.saveHistory(
          predRes.prediction, 
          predRes.confidence, 
          expRes.explanation, 
          historyImage,
          details.cost,
          details.damage
        );
      } catch (err) {
        console.error("Failed to save history:", err);
      }

    } catch (err) {
      setError(err.message || "Prediction failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadPDF = async () => {
    if (!result || !explanation || !currentFile) return;
    
    const details = getDamageDetails(formatPrediction(result.prediction));

    const fileToOptimizedBase64 = (file) => new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = (event) => {
        const img = new Image();
        img.src = event.target.result;
        img.onload = () => {
          const canvas = document.createElement('canvas');
          const MAX_WIDTH = 1024;
          let width = img.width;
          let height = img.height;
          if (width > MAX_WIDTH) { height *= MAX_WIDTH / width; width = MAX_WIDTH; }
          canvas.width = width; canvas.height = height;
          const ctx = canvas.getContext('2d');
          ctx.drawImage(img, 0, 0, width, height);
          resolve(canvas.toDataURL('image/jpeg', 0.8));
        };
      };
      reader.onerror = error => reject(error);
    });

    try {
      const base64Image = await fileToOptimizedBase64(currentFile);
      const url = await api.generateReportUrl(
        result.prediction, 
        result.confidence, 
        explanation, 
        base64Image,
        details.cost,
        details.damage
      );
      const link = document.createElement('a');
      link.href = url;
      link.download = `Damage_Report_${Date.now()}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (err) {
      console.error(err);
      setError("Failed to generate professional PDF document.");
    }
  };

  return (
    <div className="py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">AI Damage Detection Dashboard</h1>
        <p className="text-gray-400">Scan damage instantly and get AI-assisted diagnosis reports.</p>
      </div>

      {error && (
        <div className="mb-6 p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-start">
        <div>
          <UploadCard onAnalyze={handleAnalyze} loading={loading} />
        </div>
        <div>
          <ResultCard
            result={result}
            explanation={explanation}
            onDownloadPDF={handleDownloadPDF}
          />
        </div>
      </div>
    </div>
  );
}
