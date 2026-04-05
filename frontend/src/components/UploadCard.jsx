import React, { useRef, useState } from 'react';
import { UploadCloud, Image as ImageIcon, X } from 'lucide-react';

export default function UploadCard({ onAnalyze, loading }) {
  const [dragActive, setDragActive] = useState(false);
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const inputRef = useRef(null);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") setDragActive(true);
    else if (e.type === "dragleave") setDragActive(false);
  };

  const processFile = (selectedFile) => {
    if (selectedFile && selectedFile.type.startsWith('image/')) {
      setFile(selectedFile);
      const url = URL.createObjectURL(selectedFile);
      setPreview(url);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      processFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      processFile(e.target.files[0]);
    }
  };

  const handleSubmit = () => {
    if (file && onAnalyze) onAnalyze(file);
  };

  const clearFile = () => {
    setFile(null);
    setPreview(null);
  };

  return (
    <div className="glass-card p-6 h-full flex flex-col">
      <h2 className="text-xl font-semibold mb-4">Upload Vehicle Scan</h2>
      
      {!preview ? (
        <div 
          className={`relative h-[450px] flex flex-col items-center justify-center border-2 border-dashed rounded-2xl p-8 text-center transition-colors cursor-pointer ${
            dragActive ? 'border-blue-500 bg-blue-500/10' : 'border-white/20 hover:border-blue-400/50 hover:bg-white/5'
          }`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          onClick={() => inputRef.current?.click()}
        >
          <input 
            ref={inputRef} type="file" className="hidden" accept="image/*" onChange={handleChange} 
          />
          <div className="w-16 h-16 rounded-full bg-blue-500/20 flex items-center justify-center mb-4 text-blue-400">
            <UploadCloud size={32} />
          </div>
          <h3 className="text-lg font-medium text-white mb-2">Drag & Drop Image Here</h3>
          <p className="text-gray-400 text-sm">or click to browse from your device</p>
        </div>
      ) : (
        <div className="relative h-[450px] rounded-2xl overflow-hidden border border-white/10 group bg-black/20">
          <img src={preview} alt="Upload preview" className="w-full h-full object-cover" />
          <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center backdrop-blur-sm">
            <button 
              onClick={clearFile}
              className="px-4 py-2 bg-red-500/80 text-white rounded-lg flex items-center space-x-2 text-sm hover:bg-red-500"
            >
              <X size={16} /> <span>Remove</span>
            </button>
          </div>
        </div>
      )}

      <button 
        className="gradient-btn w-full mt-6 flex items-center justify-center space-x-2"
        disabled={!file || loading}
        onClick={handleSubmit}
      >
        {loading ? (
          <span className="animate-pulse">Analyzing Damage...</span>
        ) : (
          <>
            <ImageIcon size={20} />
            <span>Analyze Damage</span>
          </>
        )}
      </button>
    </div>
  );
}
