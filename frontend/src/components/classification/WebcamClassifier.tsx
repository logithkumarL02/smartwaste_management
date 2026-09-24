"use client";
import { useState, useRef, useEffect, useCallback } from "react";
import { Camera, CameraOff, Play, Square, Loader2, AlertTriangle } from "lucide-react";
import { api, ApiError } from "@/lib/api";
import type { PredictionResult } from "@/types";
import PredictionResultCard from "./PredictionResult";

const INTERVAL_MS = parseInt(process.env.NEXT_PUBLIC_WEBCAM_INTERVAL_MS ?? "3000", 10);

export default function WebcamClassifier({ token }: { token: string }) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const processingRef = useRef(false);

  const [cameraActive, setCameraActive] = useState(false);
  const [classifying, setClassifying] = useState(false);
  const [result, setResult] = useState<PredictionResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [permDenied, setPermDenied] = useState(false);
  const [processing, setProcessing] = useState(false);

  async function startCamera() {
    setError(null); setPermDenied(false);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode:"environment", width:{ideal:640}, height:{ideal:480} } });
      streamRef.current = stream;
      if (videoRef.current) { videoRef.current.srcObject = stream; await videoRef.current.play(); }
      setCameraActive(true);
    } catch (e: any) {
      if (e.name === "NotAllowedError") { setPermDenied(true); setError("Camera permission denied. Please allow camera access."); }
      else if (e.name === "NotFoundError") setError("No camera found on this device.");
      else setError(`Camera error: ${e.message}`);
    }
  }

  function stopClassifying() {
    if (intervalRef.current) { clearInterval(intervalRef.current); intervalRef.current = null; }
    setClassifying(false); setProcessing(false); processingRef.current = false;
  }

  function stopCamera() {
    stopClassifying();
    if (streamRef.current) { streamRef.current.getTracks().forEach(t => t.stop()); streamRef.current = null; }
    if (videoRef.current) videoRef.current.srcObject = null;
    setCameraActive(false); setResult(null);
  }

  const captureAndClassify = useCallback(async () => {
    if (!videoRef.current || !canvasRef.current || processingRef.current) return;
    const video = videoRef.current; const canvas = canvasRef.current;
    canvas.width = video.videoWidth || 640; canvas.height = video.videoHeight || 480;
    const ctx = canvas.getContext("2d"); if (!ctx) return;
    ctx.drawImage(video, 0, 0);
    const dataUri = canvas.toDataURL("image/jpeg", 0.85);
    processingRef.current = true; setProcessing(true);
    try {
      const res = await api.predictWebcam(dataUri, token);
      setResult(res); setError(null);
    } catch (e) {
      if (e instanceof ApiError && e.status === 503) { setError("Model not trained yet. Run: python ml/train.py"); stopClassifying(); }
    } finally { processingRef.current = false; setProcessing(false); }
  }, [token]);

  function startClassifying() {
    setClassifying(true);
    captureAndClassify();
    intervalRef.current = setInterval(captureAndClassify, INTERVAL_MS);
  }

  useEffect(() => () => stopCamera(), []);

  return (
    <div className="space-y-4">
      <div className="relative rounded-2xl overflow-hidden bg-surface-900 border border-surface-700 aspect-video flex items-center justify-center">
        <video ref={videoRef} className={cameraActive ? "w-full h-full object-cover" : "hidden"} playsInline muted />
        <canvas ref={canvasRef} className="hidden" />
        {!cameraActive && (
          <div className="text-center">
            {permDenied ? (
              <><CameraOff className="w-10 h-10 text-red-400 mx-auto mb-3" /><p className="text-sm text-red-400 font-medium">Camera access denied</p></>
            ) : (
              <><Camera className="w-10 h-10 text-slate-600 mx-auto mb-3" /><p className="text-sm text-slate-400">Camera not started</p></>
            )}
          </div>
        )}
        {cameraActive && classifying && (
          <div className="absolute top-3 left-3 flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-red-500/90 text-white text-xs font-semibold">
            <span className="w-1.5 h-1.5 rounded-full bg-white animate-pulse" />LIVE
          </div>
        )}
        {processing && (
          <div className="absolute top-3 right-3 p-1.5 rounded-lg bg-surface-900/80">
            <Loader2 className="w-4 h-4 text-brand-400 animate-spin" />
          </div>
        )}
      </div>

      {error && (
        <div className="flex items-start gap-2 p-3 rounded-xl bg-red-500/10 border border-red-500/20">
          <AlertTriangle className="w-4 h-4 text-red-400 shrink-0 mt-0.5" /><p className="text-sm text-red-400">{error}</p>
        </div>
      )}

      <div className="flex gap-3">
        {!cameraActive ? (
          <button onClick={startCamera} className="flex-1 flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl bg-brand-500 hover:bg-brand-600 text-white text-sm font-semibold transition-colors">
            <Camera className="w-4 h-4" />Start camera
          </button>
        ) : (
          <>
            <button onClick={stopCamera} className="flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl bg-surface-700 hover:bg-surface-600 text-slate-300 text-sm font-medium border border-surface-600 transition-colors">
              <CameraOff className="w-4 h-4" />Stop
            </button>
            {!classifying ? (
              <button onClick={startClassifying} className="flex-1 flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl bg-brand-500 hover:bg-brand-600 text-white text-sm font-semibold transition-colors">
                <Play className="w-4 h-4" />Start classifying
              </button>
            ) : (
              <button onClick={stopClassifying} className="flex-1 flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl bg-red-500/20 hover:bg-red-500/30 text-red-400 text-sm font-semibold border border-red-500/20 transition-colors">
                <Square className="w-4 h-4" />Stop classifying
              </button>
            )}
          </>
        )}
      </div>
      {cameraActive && <p className="text-xs text-slate-500 text-center">Captures a frame every {INTERVAL_MS/1000}s when classifying is active.</p>}
      {result && <PredictionResultCard result={result} />}
    </div>
  );
}
