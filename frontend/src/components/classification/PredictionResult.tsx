"use client";
import { AlertTriangle, CheckCircle2, Cpu, Recycle, ChevronDown } from "lucide-react";
import clsx from "clsx";
import type { PredictionResult } from "@/types";
import { getCategoryBg, getCategoryColor, getConfidenceColor, formatConfidence, CATEGORY_NAMES } from "@/lib/categories";

interface Props {
  result: PredictionResult;
  hardwareFeedback?: { success: boolean; message: string; mode: string } | null;
  onSortHardware?: () => void;
  sorting?: boolean;
}

export default function PredictionResultCard({ result, hardwareFeedback, onSortHardware, sorting }: Props) {
  const isUnknown = result.category === "unknown";
  const isLowConf = result.is_uncertain && !isUnknown;
  const pct = Math.round(result.confidence * 100);

  return (
    <div className="animate-slide-up space-y-3">
      <div className={clsx("rounded-2xl border p-5", (isUnknown || isLowConf) ? "bg-amber-500/5 border-amber-500/20" : "bg-surface-800/60 border-surface-700/50")}>
        {(isUnknown || isLowConf) && (
          <div className="flex items-center gap-2 mb-4 p-3 rounded-xl bg-amber-500/10 border border-amber-500/20">
            <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0" />
            <div>
              <p className="text-sm font-semibold text-amber-300">{isUnknown ? "Unable to classify" : "Low confidence result"}</p>
              <p className="text-xs text-amber-400/80 mt-0.5">{result.message ?? "Please verify manually before disposal."}</p>
            </div>
          </div>
        )}

        <div className="flex items-start justify-between gap-4 mb-4">
          <div>
            <p className="text-xs text-slate-500 font-medium mb-1.5">Classified as</p>
            <span className={clsx("inline-flex items-center px-3 py-1 rounded-xl text-sm font-semibold border", getCategoryBg(result.category))}>
              {result.display_name}
            </span>
          </div>
          <div className="text-right">
            <p className="text-xs text-slate-500 font-medium mb-1">Confidence</p>
            <div className="relative inline-flex items-center justify-center">
              <svg className="w-16 h-16 -rotate-90" viewBox="0 0 36 36">
                <circle cx="18" cy="18" r="15.9" fill="none" stroke="#1e293b" strokeWidth="3" />
                <circle cx="18" cy="18" r="15.9" fill="none" stroke={getCategoryColor(result.category)} strokeWidth="3"
                  strokeDasharray={`${pct} ${100-pct}`} strokeLinecap="round" />
              </svg>
              <span className={clsx("absolute text-sm font-bold", getConfidenceColor(result.confidence, result.is_uncertain))}>{pct}%</span>
            </div>
          </div>
        </div>

        <div className="mb-4">
          <div className="flex justify-between text-xs text-slate-500 mb-1">
            <span>Confidence score</span>
            <span className={getConfidenceColor(result.confidence, result.is_uncertain)}>{formatConfidence(result.confidence)}</span>
          </div>
          <div className="h-1.5 rounded-full bg-surface-700">
            <div className="h-1.5 rounded-full transition-all duration-700"
              style={{ width:`${pct}%`, background: getCategoryColor(result.category) }} />
          </div>
          <div className="flex justify-between text-[10px] text-slate-600 mt-1">
            <span>Uncertain</span><span>Low</span><span>Confident</span>
          </div>
        </div>

        {!isUnknown && (
          <div className="p-3 rounded-xl bg-surface-700/40 mb-3">
            <div className="flex items-center gap-1.5 mb-1.5">
              <Recycle className="w-3.5 h-3.5 text-brand-400" />
              <span className="text-xs font-semibold text-slate-300">Disposal recommendation</span>
            </div>
            <p className="text-sm text-slate-400 leading-relaxed">{result.recommendation}</p>
          </div>
        )}

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-surface-700/50 border border-surface-600/50">
            <Cpu className="w-3.5 h-3.5 text-slate-400" />
            <span className="text-xs font-mono text-slate-300">{result.hardware_command}</span>
          </div>
          <span className="text-xs text-slate-500">{result.model_version}</span>
        </div>
      </div>

      {isLowConf && result.alternatives && result.alternatives.length > 0 && (
        <div className="glass-card rounded-2xl p-4">
          <p className="text-xs font-semibold text-slate-400 mb-3 flex items-center gap-1.5">
            <ChevronDown className="w-3.5 h-3.5" />Top alternatives
          </p>
          <div className="space-y-2">
            {result.alternatives.map((alt, i) => (
              <div key={i} className="flex items-center gap-3">
                <span className={clsx("text-xs px-2 py-0.5 rounded-lg border font-medium", getCategoryBg(alt.category))}>
                  {CATEGORY_NAMES[alt.category] ?? alt.category}
                </span>
                <div className="flex-1 h-1 rounded-full bg-surface-700">
                  <div className="h-1 rounded-full" style={{ width:`${Math.round(alt.confidence*100)}%`, background:getCategoryColor(alt.category) }} />
                </div>
                <span className="text-xs text-slate-400 w-10 text-right">{formatConfidence(alt.confidence)}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {!isUnknown && onSortHardware && (
        <button onClick={onSortHardware} disabled={sorting}
          className="w-full flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl bg-surface-700 hover:bg-surface-600 disabled:opacity-50 text-slate-200 text-sm font-medium border border-surface-600 transition-colors">
          <Cpu className="w-4 h-4" />{sorting ? "Sending to sorter…" : "Send to hardware sorter"}
        </button>
      )}

      {hardwareFeedback && (
        <div className={clsx("flex items-center gap-2 p-3 rounded-xl text-sm border",
          hardwareFeedback.success ? "bg-brand-500/10 border-brand-500/20 text-brand-300" : "bg-red-500/10 border-red-500/20 text-red-300")}>
          {hardwareFeedback.success ? <CheckCircle2 className="w-4 h-4 shrink-0" /> : <AlertTriangle className="w-4 h-4 shrink-0" />}
          <span>{hardwareFeedback.message}</span>
          <span className="ml-auto text-xs opacity-60">[{hardwareFeedback.mode}]</span>
        </div>
      )}
    </div>
  );
}
