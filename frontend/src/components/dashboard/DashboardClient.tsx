"use client";
import { useMemo } from "react";
import Link from "next/link";
import { format, subDays, parseISO } from "date-fns";
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid } from "recharts";
import { ScanLine, TrendingUp, AlertTriangle, CheckCircle2, ArrowRight } from "lucide-react";
import { CATEGORY_COLORS, CATEGORY_NAMES, formatConfidence, getCategoryBg } from "@/lib/categories";
import type { PredictionHistoryItem } from "@/types";
import clsx from "clsx";

export default function DashboardClient({ predictions, displayName }: { predictions: PredictionHistoryItem[]; displayName: string }) {
  const stats = useMemo(() => {
    const total = predictions.length;
    const uncertain = predictions.filter(p => p.is_uncertain).length;
    const byCategory: Record<string, number> = {};
    predictions.forEach(p => { byCategory[p.category] = (byCategory[p.category] ?? 0) + 1; });
    return { total, uncertain, confident: total - uncertain, byCategory };
  }, [predictions]);

  const pieData = useMemo(() =>
    Object.entries(stats.byCategory).sort((a,b) => b[1]-a[1]).map(([cat, count]) => ({
      name: CATEGORY_NAMES[cat] ?? cat, value: count, color: CATEGORY_COLORS[cat] ?? "#64748b",
    })), [stats.byCategory]);

  const activityData = useMemo(() => {
    const days = Array.from({ length: 7 }, (_, i) => {
      const date = subDays(new Date(), 6 - i);
      return { date: format(date, "MMM d"), key: format(date, "yyyy-MM-dd"), count: 0 };
    });
    predictions.forEach(p => {
      const entry = days.find(d => d.key === p.created_at.slice(0, 10));
      if (entry) entry.count++;
    });
    return days;
  }, [predictions]);

  const recent = predictions.slice(0, 6);

  return (
    <div className="animate-fade-in space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-100">Good day, {displayName}</h1>
          <p className="text-slate-400 text-sm mt-1">Your waste classification overview.</p>
        </div>
        <Link href="/classify" className="hidden sm:flex items-center gap-2 px-4 py-2 rounded-xl bg-brand-500 hover:bg-brand-600 text-white text-sm font-semibold transition-colors">
          <ScanLine className="w-4 h-4" />Classify waste
        </Link>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label:"Total scans", value:stats.total, icon:<ScanLine className="w-4 h-4 text-brand-400"/>, bg:"bg-brand-500/5 border-brand-500/10" },
          { label:"Confident", value:stats.confident, icon:<CheckCircle2 className="w-4 h-4 text-emerald-400"/>, bg:"bg-emerald-500/5 border-emerald-500/10" },
          { label:"Uncertain", value:stats.uncertain, icon:<AlertTriangle className="w-4 h-4 text-amber-400"/>, bg:"bg-amber-500/5 border-amber-500/10" },
          { label:"Categories", value:Object.keys(stats.byCategory).length, icon:<TrendingUp className="w-4 h-4 text-blue-400"/>, bg:"bg-blue-500/5 border-blue-500/10" },
        ].map(({ label, value, icon, bg }) => (
          <div key={label} className={clsx("rounded-2xl p-4 border", bg)}>
            <div className="flex items-center gap-2 mb-2">{icon}<span className="text-xs text-slate-500 font-medium">{label}</span></div>
            <p className="text-2xl font-bold text-slate-100">{value.toLocaleString()}</p>
          </div>
        ))}
      </div>

      {stats.total > 0 ? (
        <div className="grid lg:grid-cols-2 gap-4">
          <div className="glass-card rounded-2xl p-5">
            <h2 className="text-sm font-semibold text-slate-300 mb-4">Category breakdown</h2>
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie data={pieData} cx="50%" cy="50%" innerRadius={55} outerRadius={80} paddingAngle={3} dataKey="value">
                  {pieData.map((entry, i) => <Cell key={i} fill={entry.color} />)}
                </Pie>
                <Tooltip contentStyle={{ background:"#1e293b", border:"1px solid #334155", borderRadius:"10px", fontSize:"12px" }} />
              </PieChart>
            </ResponsiveContainer>
            <div className="mt-2 grid grid-cols-2 gap-1.5">
              {pieData.slice(0,6).map(entry => (
                <div key={entry.name} className="flex items-center gap-1.5">
                  <div className="w-2 h-2 rounded-full shrink-0" style={{ background: entry.color }} />
                  <span className="text-xs text-slate-400 truncate">{entry.name}</span>
                  <span className="text-xs text-slate-500 ml-auto">{entry.value}</span>
                </div>
              ))}
            </div>
          </div>
          <div className="glass-card rounded-2xl p-5">
            <h2 className="text-sm font-semibold text-slate-300 mb-4">Activity (last 7 days)</h2>
            <ResponsiveContainer width="100%" height={240}>
              <BarChart data={activityData} barSize={20}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="date" tick={{ fill:"#64748b", fontSize:11 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill:"#64748b", fontSize:11 }} axisLine={false} tickLine={false} allowDecimals={false} />
                <Tooltip contentStyle={{ background:"#1e293b", border:"1px solid #334155", borderRadius:"10px", fontSize:"12px" }} />
                <Bar dataKey="count" fill="#22c55e" name="Scans" radius={[4,4,0,0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      ) : (
        <div className="glass-card rounded-2xl p-10 text-center">
          <ScanLine className="w-10 h-10 text-slate-600 mx-auto mb-3" />
          <h3 className="text-slate-300 font-semibold mb-1">No classifications yet</h3>
          <p className="text-slate-500 text-sm mb-5">Upload a waste image or use your webcam to get started.</p>
          <Link href="/classify" className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-brand-500 hover:bg-brand-600 text-white text-sm font-semibold transition-colors">
            Classify your first item<ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      )}

      {recent.length > 0 && (
        <div className="glass-card rounded-2xl p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-semibold text-slate-300">Recent classifications</h2>
            <Link href="/history" className="text-xs text-brand-400 hover:text-brand-300 flex items-center gap-1">View all<ArrowRight className="w-3 h-3" /></Link>
          </div>
          <div className="space-y-2">
            {recent.map(item => (
              <div key={item.id} className="flex items-center gap-3 px-3 py-2.5 rounded-xl bg-surface-700/30 hover:bg-surface-700/50 transition-colors">
                <span className={clsx("text-xs px-2 py-0.5 rounded-lg border font-medium", getCategoryBg(item.category))}>
                  {CATEGORY_NAMES[item.category] ?? item.category}
                </span>
                {item.is_uncertain && <AlertTriangle className="w-3 h-3 text-amber-400 shrink-0" />}
                <span className="text-sm text-slate-300 font-medium ml-auto">{formatConfidence(item.confidence)}</span>
                <span className="text-xs text-slate-500 hidden sm:block">{format(parseISO(item.created_at), "MMM d, HH:mm")}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
