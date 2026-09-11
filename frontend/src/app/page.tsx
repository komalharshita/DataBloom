"use client";

import React, { useState } from 'react';
import axios from 'axios';
import dynamic from 'next/dynamic';
import { Upload, FileText, AlertCircle, BarChart3, Loader2 } from 'lucide-react';

// Dynamically import Plotly to avoid SSR issues
const Plot = dynamic(() => import('react-plotly.js'), { ssr: false });

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<any | null>(null);
  const [uploadProgress, setUploadProgress] = useState(0);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
    }
  };

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;

    setLoading(true);
    setError(null);
    setResults(null);
    setUploadProgress(0);

    const formData = new FormData();
    formData.append("file", file);
    if (question) {
      formData.append("question", question);
    }

    try {
      const response = await axios.post("http://localhost:8000/api/analyze", formData, {
        headers: { "Content-Type": "multipart/form-data" },
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / (progressEvent.total || 1));
          setUploadProgress(percentCompleted);
        }
      });
      setResults(response.data);
    } catch (err: any) {
      console.error(err);
      setError(err.response?.data?.detail || err.message || "An error occurred during analysis.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <header className="bg-white border-b border-slate-200 px-6 py-4 shadow-sm">
        <div className="max-w-6xl mx-auto flex items-center gap-2">
          <BarChart3 className="text-blue-600 h-6 w-6" />
          <h1 className="text-xl font-bold">AI Data Storyteller</h1>
        </div>
      </header>

      <main className="max-w-6xl mx-auto p-6 space-y-8">
        {/* Upload Section */}
        <section className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
          <h2 className="text-lg font-semibold mb-4">Start your analysis</h2>
          <form onSubmit={handleAnalyze} className="space-y-4">
            <div className="flex flex-col md:flex-row gap-4">
              <div className="flex-1">
                <label className="block text-sm font-medium text-slate-700 mb-1">
                  Upload Dataset (CSV, JSON, Excel)
                </label>
                <div className="flex items-center justify-center w-full">
                  <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-slate-300 border-dashed rounded-lg cursor-pointer bg-slate-50 hover:bg-slate-100">
                    <div className="flex flex-col items-center justify-center pt-5 pb-6">
                      <Upload className="w-8 h-8 mb-2 text-slate-500" />
                      <p className="text-sm text-slate-500">
                        <span className="font-semibold">Click to upload</span> or drag and drop
                      </p>
                      {file && (
                        <p className="mt-2 text-sm font-medium text-blue-600">
                          {file.name} ({(file.size / 1024).toFixed(2)} KB)
                        </p>
                      )}
                    </div>
                    <input type="file" className="hidden" accept=".csv,.json,.xlsx,.xls" onChange={handleFileChange} />
                  </label>
                </div>
              </div>
              <div className="flex-1">
                <label className="block text-sm font-medium text-slate-700 mb-1">
                  Analytical Question (Optional)
                </label>
                <textarea
                  className="w-full h-32 p-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="e.g., What are the main trends in revenue? Or leave blank for exploratory analysis."
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                />
              </div>
            </div>
            <button
              type="submit"
              disabled={!file || loading}
              className="w-full md:w-auto px-6 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Analyzing Data ({uploadProgress}%)
                </>
              ) : (
                "Generate Story"
              )}
            </button>
          </form>
          {error && (
            <div className="mt-4 p-4 bg-red-50 text-red-700 rounded-lg flex items-start gap-2 border border-red-200">
              <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
              <p>{error}</p>
            </div>
          )}
        </section>

        {/* Results Section */}
        {results && (
          <div className="space-y-6">
            {/* Executive Summary */}
            <section className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
              <h2 className="text-xl font-bold flex items-center gap-2 mb-4">
                <FileText className="w-6 h-6 text-blue-600" /> Executive Summary
              </h2>
              <p className="text-slate-700 leading-relaxed text-lg">{results.summary}</p>
            </section>

            {/* Key Metrics */}
            <section className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {results.key_metrics?.map((metric: any, i: number) => (
                <div key={i} className="bg-white p-4 rounded-xl shadow-sm border border-slate-200">
                  <p className="text-sm text-slate-500 font-medium">{metric.name}</p>
                  <p className="text-2xl font-bold text-slate-900 mt-1">{metric.value}</p>
                </div>
              ))}
            </section>

            {/* Visualizations & Insights */}
            <section className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {results.visualizations?.map((viz: any, i: number) => {
                const isPie = viz.type === 'pie';
                const trace = isPie ? {
                  labels: viz.x_data,
                  values: viz.y_data,
                  type: 'pie' as const,
                  name: viz.title
                } : {
                  x: viz.x_data,
                  y: viz.y_data,
                  type: viz.type as any,
                  name: viz.title,
                  marker: { color: '#2563eb' }
                };
                
                return (
                  <div key={i} className="bg-white p-6 rounded-xl shadow-sm border border-slate-200 flex flex-col">
                    <h3 className="font-bold text-lg mb-2">{viz.title}</h3>
                    <div className="h-64 bg-slate-50 rounded flex items-center justify-center mb-4 border border-slate-100 overflow-hidden relative">
                      {viz.x_data && viz.x_data.length > 0 ? (
                        <Plot
                          data={[trace]}
                          layout={{ 
                            autosize: true, 
                            margin: { t: 10, b: 30, l: 40, r: 10 },
                            xaxis: { title: viz.x, automargin: true },
                            yaxis: { title: viz.y, automargin: true },
                            showlegend: false
                          }}
                          useResizeHandler={true}
                          style={{ width: '100%', height: '100%' }}
                          config={{ displayModeBar: false }}
                        />
                      ) : (
                        <p className="text-sm text-slate-500">Could not render chart data</p>
                      )}
                    </div>
                    <div className="mt-auto bg-blue-50 p-3 rounded-lg border border-blue-100">
                      <p className="text-sm text-blue-800"><span className="font-semibold">Insight:</span> {viz.insight}</p>
                    </div>
                  </div>
                );
              })}
            </section>

            {/* Additional Insights & Recommendations */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <section className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
                <h3 className="font-bold text-lg mb-4">Key Insights</h3>
                <ul className="space-y-2">
                  {results.insights?.map((insight: string, i: number) => (
                    <li key={i} className="flex items-start gap-2 text-slate-700">
                      <span className="text-blue-500 mt-1">•</span> {insight}
                    </li>
                  ))}
                </ul>
              </section>

              <section className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
                <h3 className="font-bold text-lg mb-4">Recommendations</h3>
                <ul className="space-y-2">
                  {results.recommendations?.map((rec: string, i: number) => (
                    <li key={i} className="flex items-start gap-2 text-slate-700">
                      <span className="text-green-500 mt-1">•</span> {rec}
                    </li>
                  ))}
                </ul>
              </section>
            </div>

            {/* Data Quality */}
            {results.data_quality?.length > 0 && (
              <section className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
                <h3 className="font-bold text-lg mb-4 text-orange-600 flex items-center gap-2">
                  <AlertCircle className="w-5 h-5" /> Data Quality Notices
                </h3>
                <div className="space-y-3">
                  {results.data_quality.map((dq: any, i: number) => (
                    <div key={i} className={`p-3 rounded-lg text-sm ${dq.severity === 'high' ? 'bg-red-50 text-red-800 border border-red-200' : dq.severity === 'medium' ? 'bg-orange-50 text-orange-800 border border-orange-200' : 'bg-slate-50 text-slate-700 border border-slate-200'}`}>
                      <span className="font-semibold capitalize">{dq.severity} Severity:</span> {dq.issue}
                    </div>
                  ))}
                </div>
              </section>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
