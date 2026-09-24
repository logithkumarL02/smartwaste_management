"use client";
import { useState } from "react";
import { Upload, Camera } from "lucide-react";
import clsx from "clsx";
import UploadClassifier from "./UploadClassifier";
import WebcamClassifier from "./WebcamClassifier";

type Tab = "upload" | "webcam";

export default function ClassifyClient({ token }: { token: string }) {
  const [tab, setTab] = useState<Tab>("upload");
  return (
    <div className="animate-fade-in max-w-2xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-slate-100">Classify Waste</h1>
        <p className="text-slate-400 text-sm mt-1">Upload an image or use your webcam to identify and sort waste.</p>
      </div>
      <div className="flex gap-1 p-1 rounded-xl bg-surface-800 border border-surface-700 mb-6">
        {(["upload", "webcam"] as Tab[]).map(t => (
          <button key={t} onClick={() => setTab(t)}
            className={clsx("flex-1 flex items-center justify-center gap-2 py-2.5 rounded-lg text-sm font-medium transition-all",
              tab === t ? "bg-brand-500 text-white shadow-sm" : "text-slate-400 hover:text-slate-200")}>
            {t === "upload" ? <Upload className="w-4 h-4" /> : <Camera className="w-4 h-4" />}
            {t === "upload" ? "Upload Image" : "Webcam"}
          </button>
        ))}
      </div>
      {tab === "upload" ? <UploadClassifier token={token} /> : <WebcamClassifier token={token} />}
    </div>
  );
}
