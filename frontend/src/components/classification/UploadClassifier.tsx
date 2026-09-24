"use client";
import { useState, useRef, useCallback } from "react";
import { Upload, X, Loader2, ImageIcon } from "lucide-react";
import { api, ApiError } from "@/lib/api";
import type { PredictionResult } from "@/types";
import PredictionResultCard from "./PredictionResult";
import clsx from "clsx";

const ALLOWED = ["image/jpeg", "image/png", "image/webp", "image/bmp"];
const MAX_MB = 10;

export default function UploadClassifier({ token }: { token: string }) {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<PredictionResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [dragging, setDragging] = useState(false);
  const [hwFeedback, setHwFeedback] = useState<any>(null);
  const [sorting, setSorting] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  function handleFile(f: File) {
    if (!ALLOWED.includes(f.type)) return setError(`Unsupported type: ${f.type}. Use JPEG, PNG, WebP, or BMP.`);
    if (f.size > MAX_MB * 1024 * 1024) return setError(`File too large (max ${MAX_MB} MB).`);
    setError(null); setResult(null); setHwFeedback(null);
    setFile(f); setPreview(URL.createObjectURL(f));
  }

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault(); setDragging(false);
    const f = e.dataTransfer.files[0]; if (f) handleFile(f);
  }, []);

  function clear() {
    setFile(null); setPreview(null); setResult(null); setError(null); setHwFeedback(null);
    if (inputRef.current) inputRef.current.value = "";
  }

  async function classify() {
    if (!file) return;
    setLoading(true); setError(null); setResult(null); setHwFeedback(null);
    try {
      setResult(await api.predict(file, token));
    } catch (e) {
      if (e instanceof ApiError && e.status === 503) setError("Model not trained yet. Run: python ml/train.py");
      else if (e instanceof ApiError) setError(e.message);
      else setError("Classification failed. Check the backend is running.");
    } finally { setLoading(false); }
  }

  async function handleSort() {
    if (!result) return;
    setSorting(true);
    try { setHwFeedback(await api.sort(result.hardware_command, token)); }
    catch { setHwFeedback({ success: false, message: "Hardware sort failed.", mode: "unknown" }); }
    finally { setSorting(false); }
  }

  return (
    <div className="space-y-4">
      {!file ? (
        <div onClick={() => inputRef.current?.click()}
          onDragOver={e => { e.preventDefault(); setDragging(true); }}
          onDragLeave={() => setDragging(false)} onDrop={handleDrop}
          className={clsx("border-2 border-dashed rounded-2xl p-10 text-center cursor-pointer transition-all",
            dragging ? "border-brand-500 bg-brand-500/5" : "border-surface-600 hover:border-surface-500 bg-surface-800/30")}>
          <input ref={inputRef} type="file" accept={ALLOWED.join(",")} onChange={e => { const f = e.target.files?.[0]; if(f) handleFile(f); }} className="hidden" />
          <Upload className="w-8 h-8 text-slate-500 mx-auto mb-3" />
          <p className="text-sm font-medium text-slate-300">Drop an image here, or <span className="text-brand-400">browse</span></p>
          <p className="text-xs text-slate-500 mt-1">JPEG, PNG, WebP, BMP — max {MAX_MB} MB</p>
        </div>
      ) : (
        <div className="relative rounded-2xl overflow-hidden bg-surface-800 border border-surface-700">
          <img src={preview!} alt="Preview" className="w-full max-h-72 object-contain" />
          <button onClick={clear} className="absolute top-3 right-3 p-1.5 rounded-lg bg-surface-900/80 text-slate-300 hover:text-white transition-colors">
            <X className="w-4 h-4" />
          </button>
          <div className="px-4 py-2 border-t border-surface-700 flex items-center gap-2">
            <ImageIcon className="w-3.5 h-3.5 text-slate-500" />
            <span className="text-xs text-slate-400 truncate">{file.name}</span>
            <span className="text-xs text-slate-500 ml-auto">{(file.size/1024/1024).toFixed(2)} MB</span>
          </div>
        </div>
      )}

      {error && <div className="p-3 rounded-xl bg-red-500/10 border border-red-500/20 text-sm text-red-400">{error}</div>}

      {file && !result && (
        <button onClick={classify} disabled={loading}
          className="w-full flex items-center justify-center gap-2 py-3 px-4 rounded-xl bg-brand-500 hover:bg-brand-600 disabled:opacity-60 text-white text-sm font-semibold transition-colors">
          {loading ? <><Loader2 className="w-4 h-4 animate-spin" />Classifying…</> : "Classify waste"}
        </button>
      )}

      {result && <PredictionResultCard result={result} onSortHardware={handleSort} hardwareFeedback={hwFeedback} sorting={sorting} />}
      {result && (
        <button onClick={clear} className="w-full py-2.5 px-4 rounded-xl border border-surface-600 text-slate-400 hover:text-slate-200 text-sm transition-colors">
          Classify another item
        </button>
      )}
    </div>
  );
}
