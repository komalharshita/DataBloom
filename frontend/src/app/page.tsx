"use client";

import { FormEvent, useRef, useState } from "react";
import axios from "axios";
import dynamic from "next/dynamic";
import { AlertCircle, ArrowUpRight, BarChart3, Check, ChevronRight, CircleHelp, FileSpreadsheet, Leaf, Loader2, MessageCircle, Sparkles, Upload } from "lucide-react";

const Plot = dynamic(() => import("react-plotly.js"), { ssr: false });
const API_URL = "http://localhost:8000/api/analyze";

type Visualization = { title: string; type: string; x: string; y?: string; x_data?: unknown[]; y_data?: unknown[]; insight?: string; rationale?: string };
type Result = { summary?: string; executive_summary?: string; key_metrics?: { name: string; value: string }[]; visualizations?: Visualization[]; insights?: string[]; recommendations?: string[]; data_quality?: { issue: string; severity: string }[]; overview?: { rows?: number } };

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [dragging, setDragging] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<Result | null>(null);
  const [progress, setProgress] = useState(0);
  const uploadRef = useRef<HTMLElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const chooseFile = (nextFile?: File) => {
    if (!nextFile) return;
    if (![".csv", ".json", ".xlsx", ".xls"].some((ext) => nextFile.name.toLowerCase().endsWith(ext))) {
      setError("That file type is not supported. Choose a CSV, XLSX, or JSON file.");
      return;
    }
    setFile(nextFile);
    setError(null);
  };

  const analyze = async (event: FormEvent) => {
    event.preventDefault();
    if (!file) { setError("Choose a dataset before starting your story."); return; }
    setLoading(true); setError(null); setResults(null); setProgress(0);
    const data = new FormData();
    data.append("file", file);
    if (question.trim()) data.append("question", question.trim());
    try {
      const response = await axios.post<Result>(API_URL, data, {
        headers: { "Content-Type": "multipart/form-data" },
        onUploadProgress: (event) => setProgress(Math.round((event.loaded * 100) / (event.total || 1))),
      });
      setResults(response.data);
      window.setTimeout(() => document.getElementById("results")?.scrollIntoView({ behavior: "smooth" }), 80);
    } catch (err: unknown) {
      const detail = axios.isAxiosError(err) ? err.response?.data?.detail : null;
      setError(detail || "Something went wrong while analyzing your dataset. Check the file and try again.");
    } finally { setLoading(false); }
  };

  const anotherQuestion = () => { setResults(null); setError(null); uploadRef.current?.scrollIntoView({ behavior: "smooth", block: "center" }); };
  const scrollToUpload = () => uploadRef.current?.scrollIntoView({ behavior: "smooth" });

  return <main className="app-shell">
    <nav className="nav-bar" aria-label="Main navigation">
      <button className="brand" onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })} aria-label="DataBloom home"><span className="brand-mark"><Leaf size={17} /></span><span>DataBloom</span></button>
      <div className="nav-links"><a href="#how-it-works">How it works</a><a href="#story">Your story</a></div>
      <button className="nav-cta" onClick={scrollToUpload}>Get started <ArrowUpRight size={15} /></button>
    </nav>

    {!results && <section className="hero" aria-labelledby="hero-title">
      <div className="hero-copy"><p className="eyebrow"><Sparkles size={14} /> AI-powered data storytelling</p><h1 id="hero-title">Turn raw data into a story people can understand.</h1><p className="hero-description">Upload your data, ask a question, and let DataBloom uncover the trends, patterns, and insights that matter.</p><div className="hero-actions"><button className="button button-primary" onClick={scrollToUpload}>Start analyzing <ChevronRight size={17} /></button><a className="text-link" href="#how-it-works">See how it works <ArrowUpRight size={15} /></a></div><div className="trust-line"><span><Check size={14} /> Grounded in your data</span><span><Check size={14} /> No dashboard expertise needed</span></div></div>
      <Preview />
    </section>}

    <section className={results ? "workspace workspace-results" : "workspace"} ref={uploadRef} id="story">
      {!results && <div className="section-intro"><div><p className="eyebrow">01 / Start with your data</p><h2>Your story starts here.</h2></div><p>Bring a dataset and a curious question. DataBloom will turn the rows into a clear, visual narrative.</p></div>}
      <form className="analysis-form" onSubmit={analyze}>
        <div className="upload-panel"><PanelHeading eyebrow="Dataset" title="Drop your dataset here" icon={<FileSpreadsheet size={23} />} /><label className={`drop-zone ${dragging ? "is-dragging" : ""} ${file ? "has-file" : ""}`} onDragOver={(event) => { event.preventDefault(); setDragging(true); }} onDragLeave={() => setDragging(false)} onDrop={(event) => { event.preventDefault(); setDragging(false); chooseFile(event.dataTransfer.files[0]); }}><input ref={inputRef} type="file" accept=".csv,.json,.xlsx,.xls" onChange={(event) => chooseFile(event.target.files?.[0])} /><span className="upload-icon">{file ? <Check size={22} /> : <Upload size={22} />}</span><strong>{file ? file.name : "Drag and drop your file"}</strong><small>{file ? `${(file.size / 1024).toFixed(1)} KB · Ready to analyze` : "CSV, XLSX or JSON · up to 20 MB"}</small><span className="change-file">{file ? "Choose a different file" : "or choose a file"}</span></label></div>
        <div className="question-panel"><PanelHeading eyebrow="Your question" title="What do you want to know?" icon={<CircleHelp size={22} />} /><textarea value={question} onChange={(event) => setQuestion(event.target.value)} placeholder="Try: Which region is growing fastest?" aria-label="Analytical question" /><div className="question-footer"><span>Leave blank for an exploratory story.</span><button className="button button-primary" type="submit" disabled={loading}>{loading ? <><Loader2 size={17} className="spin" /> Analyzing {progress}%</> : <>Generate my story <ChevronRight size={17} /></>}</button></div></div>
      </form>
      {loading && <div className="loading-state" aria-live="polite"><span className="loading-orb"><Sparkles size={22} /></span><div><strong>Finding the story in your data...</strong><p>Reading your file and calculating the patterns that answer your question.</p></div><Loader2 size={19} className="spin loading-spinner" /></div>}
      {error && <div className="error-state" role="alert"><AlertCircle size={20} /><div><strong>We couldn&apos;t build that story.</strong><p>{error}</p></div><button type="button" onClick={() => setError(null)} aria-label="Dismiss error">&times;</button></div>}
    </section>

    {results && <Results result={results} onAnotherQuestion={anotherQuestion} />}
    {!results && <HowItWorks />}
    <footer><span className="brand"><span className="brand-mark"><Leaf size={15} /></span>DataBloom</span><span>Make data feel human.</span></footer>
  </main>;
}

function PanelHeading({ eyebrow, title, icon }: { eyebrow: string; title: string; icon: React.ReactNode }) { return <div className="panel-heading"><div><p className="eyebrow">{eyebrow} {eyebrow === "Your question" && <span>Optional</span>}</p><h2>{title}</h2></div><span className="heading-icon">{icon}</span></div>; }
function Preview() { return <div className="hero-preview" aria-label="Preview of an analysis story"><div className="preview-window"><div className="preview-top"><span className="preview-dots"><i /><i /><i /></span><span className="preview-label">DataBloom / story</span><span className="preview-status"><span /> Live analysis</span></div><div className="preview-body"><p className="mini-eyebrow">Your data, translated</p><h2>A clearer view of what&apos;s growing.</h2><div className="preview-metrics"><div><small>Total revenue</small><strong>$1.24M</strong><span>+18.4%</span></div><div><small>Top segment</small><strong>Software</strong><span>by revenue</span></div></div><div className="preview-chart"><div className="chart-lines"><span /><span /><span /><span /></div><svg viewBox="0 0 460 126" role="img" aria-label="Rising trend preview"><path d="M4 112 C55 96 67 102 105 84 S163 94 200 63 S257 74 293 42 S354 56 387 29 S429 34 455 8" fill="none" stroke="currentColor" strokeWidth="4" strokeLinecap="round" /><circle cx="455" cy="8" r="6" fill="currentColor" /></svg><div className="chart-labels"><span>Jan</span><span>Feb</span><span>Mar</span><span>Apr</span><span>May</span></div></div><div className="preview-note"><Sparkles size={15} /><span><b>Story signal</b> Revenue is building momentum across the period.</span></div></div></div><div className="floating-note"><span className="note-icon"><MessageCircle size={16} /></span><span><b>Ask your data</b><small>What changed this quarter?</small></span></div></div>; }
function HowItWorks() { return <section className="how-section" id="how-it-works"><p className="eyebrow">02 / How it works</p><h2>From rows to a reason to care.</h2><div className="steps"><div><span>01</span><h3>Bring your data</h3><p>Upload the file you already have. No cleanup ritual required.</p></div><div><span>02</span><h3>Ask naturally</h3><p>Point DataBloom toward the question behind the numbers.</p></div><div><span>03</span><h3>See the story</h3><p>Get evidence-led charts, insights, and ideas for what to explore next.</p></div></div></section>; }

function Results({ result, onAnotherQuestion }: { result: Result; onAnotherQuestion: () => void }) {
  return <section className="results-wrap" id="results"><div className="results-header"><div><p className="eyebrow"><Sparkles size={14} /> 03 / Your story</p><h1>Here&apos;s what DataBloom found.</h1><p>A visual story generated from your dataset{result.overview?.rows ? ` · ${result.overview.rows} rows explored` : ""}.</p></div><button className="button button-secondary" onClick={onAnotherQuestion}><MessageCircle size={16} /> Ask another question</button></div><section className="summary-section"><div className="summary-label"><span className="signal-dot" /> The big picture</div><p>{result.summary || result.executive_summary || "Your data story is ready."}</p></section><Metrics metrics={result.key_metrics} /><Charts visualizations={result.visualizations} /><div className="insights-grid"><ListSection className="insights-section" eyebrow="What stands out" title="Key insights" items={result.insights} /><ListSection className="recommendations-section" eyebrow="Keep exploring" title="What you could explore next" items={result.recommendations} /></div><Quality items={result.data_quality} /></section>;
}
function Metrics({ metrics }: { metrics?: Result["key_metrics"] }) { if (!metrics?.length) return null; return <section className="metrics-grid" aria-label="Key metrics">{metrics.slice(0, 4).map((metric, index) => <div className={`metric-card metric-${index}`} key={`${metric.name}-${index}`}><small>{metric.name}</small><strong>{metric.value}</strong><span>{index === 0 ? "Calculated from your file" : "Data-backed measure"}</span></div>)}</section>; }
function Charts({ visualizations }: { visualizations?: Visualization[] }) { if (!visualizations?.length) return null; return <section className="results-section"><div className="results-section-heading"><div><p className="eyebrow">Evidence</p><h2>Let&apos;s look closer.</h2></div><span>Charts selected for the shape of your data</span></div><div className="charts-grid">{visualizations.map((viz, index) => <ChartCard key={`${viz.title}-${index}`} viz={viz} />)}</div></section>; }
function ChartCard({ viz }: { viz: Visualization }) { const isPie = viz.type === "pie"; const trace = isPie ? { labels: viz.x_data, values: viz.y_data, type: "pie" as const, marker: { colors: ["#ec6b9a", "#1d594a", "#e9b44c", "#8ab5a8"] } } : { x: viz.x_data, y: viz.y_data, type: viz.type as "bar" | "line" | "scatter" | "histogram", marker: { color: "#1d594a" }, line: { color: "#1d594a", width: 3 } }; return <article className="chart-card"><div className="chart-card-heading"><div><h3>{viz.title}</h3><p>{viz.rationale || "A view selected to make the pattern easier to see."}</p></div><BarChart3 size={19} /></div><div className="plot-wrap">{viz.x_data?.length ? <Plot data={[trace]} layout={{ autosize: true, margin: { t: 10, b: 42, l: 48, r: 12 }, paper_bgcolor: "transparent", plot_bgcolor: "transparent", font: { family: "DM Sans, sans-serif", color: "#52645e", size: 11 }, xaxis: { title: viz.x, automargin: true, gridcolor: "#e5eee9" }, yaxis: { title: viz.y, automargin: true, gridcolor: "#e5eee9" }, showlegend: false }} useResizeHandler style={{ width: "100%", height: "100%" }} config={{ displayModeBar: false }} /> : <p className="chart-empty">Chart data is not available for this view.</p>}</div>{viz.insight && <p className="chart-insight"><Sparkles size={14} /> {viz.insight}</p>}</article>; }
function ListSection({ className, eyebrow, title, items }: { className: string; eyebrow: string; title: string; items?: string[] }) { return <section className={className}><div className="results-section-heading"><div><p className="eyebrow">{eyebrow}</p><h2>{title}</h2></div></div><div className="insight-list">{(items || []).map((item, index) => <div className="insight-item" key={`${item}-${index}`}><span>{String(index + 1).padStart(2, "0")}</span><p>{item}</p></div>)}</div></section>; }
function Quality({ items }: { items?: { issue: string; severity: string }[] }) { if (!items?.length) return null; return <section className="quality-section"><div><p className="eyebrow">A note on the data</p><h2>Data quality</h2></div><div className="quality-list">{items.map((item, index) => <div key={`${item.issue}-${index}`} className={`quality-item ${item.severity}`}><AlertCircle size={16} /><span><b>{item.severity}:</b> {item.issue}</span></div>)}</div></section>; }
