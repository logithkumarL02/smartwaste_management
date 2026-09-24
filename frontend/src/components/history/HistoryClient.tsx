"use client";
import { useState, useMemo } from "react";
import { format, parseISO } from "date-fns";
import { Search, Filter, AlertTriangle, History, ScanLine } from "lucide-react";
import clsx from "clsx";
import Link from "next/link";
import type { PredictionHistoryItem } from "@/types";
import { CATEGORY_NAMES, getCategoryBg, formatConfidence, getConfidenceColor } from "@/lib/categories";

const ALL_CATS = ["plastic","metal","glass","paper_cardboard","organic","e_waste","textile","other","unknown"];
const PAGE_SIZE = 15;

export default function HistoryClient({ predictions }: { predictions: PredictionHistoryItem[] }) {
  const [search, setSearch] = useState("");
  const [filterCat, setFilterCat] = useState("all");
  const [filterSrc, setFilterSrc] = useState("all");
  const [filterUnc, setFilterUnc] = useState("all");
  const [page, setPage] = useState(1);

  const filtered = useMemo(() => predictions.filter(p => {
    if (filterCat !== "all" && p.category !== filterCat) return false;
    if (filterSrc !== "all" && p.source !== filterSrc) return false;
    if (filterUnc === "uncertain" && !p.is_uncertain) return false;
    if (filterUnc === "confident" && p.is_uncertain) return false;
    if (search) {
      const q = search.toLowerCase();
      if (!(CATEGORY_NAMES[p.category]??p.category).toLowerCase().includes(q) && !p.hardware_command.toLowerCase().includes(q)) return false;
    }
    return true;
  }), [predictions, filterCat, filterSrc, filterUnc, search]);

  const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const paginated = filtered.slice((page-1)*PAGE_SIZE, page*PAGE_SIZE);
  const reset = () => setPage(1);

  if (!predictions.length) return (
    <div className="animate-fade-in max-w-3xl mx-auto">
      <h1 className="text-2xl font-bold text-slate-100 mb-6">History</h1>
      <div className="glass-card rounded-2xl p-12 text-center">
        <History className="w-10 h-10 text-slate-600 mx-auto mb-3" />
        <h3 className="text-slate-300 font-semibold mb-1">No predictions yet</h3>
        <p className="text-slate-500 text-sm mb-5">Your classification history will appear here.</p>
        <Link href="/classify" className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-brand-500 hover:bg-brand-600 text-white text-sm font-semibold transition-colors">
          <ScanLine className="w-4 h-4" />Start classifying
        </Link>
      </div>
    </div>
  );

  return (
    <div className="animate-fade-in max-w-4xl mx-auto space-y-5">
      <div>
        <h1 className="text-2xl font-bold text-slate-100">History</h1>
        <p className="text-slate-400 text-sm mt-1">{predictions.length} classification{predictions.length!==1?"s":""} total</p>
      </div>
      <div className="glass-card rounded-2xl p-4 space-y-3">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
          <input type="text" placeholder="Search category or command…" value={search}
            onChange={e => { setSearch(e.target.value); reset(); }}
            className="w-full pl-9 pr-4 py-2.5 rounded-xl bg-surface-700 border border-surface-600 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-brand-500 transition-colors" />
        </div>
        <div className="flex flex-wrap gap-2 items-center">
          <Filter className="w-3.5 h-3.5 text-slate-500 shrink-0" />
          {[
            { val:filterCat, set:(v:string)=>{setFilterCat(v);reset();}, opts:[["all","All categories"],...ALL_CATS.map(c=>[c,CATEGORY_NAMES[c]??c])] },
            { val:filterSrc, set:(v:string)=>{setFilterSrc(v);reset();}, opts:[["all","All sources"],["upload","Upload"],["webcam","Webcam"]] },
            { val:filterUnc, set:(v:string)=>{setFilterUnc(v);reset();}, opts:[["all","All results"],["confident","Confident"],["uncertain","Uncertain"]] },
          ].map((sel, i) => (
            <select key={i} value={sel.val} onChange={e => sel.set(e.target.value)}
              className="text-xs px-3 py-1.5 rounded-lg bg-surface-700 border border-surface-600 text-slate-300 focus:outline-none focus:border-brand-500 transition-colors cursor-pointer">
              {sel.opts.map(([v,l]) => <option key={v} value={v}>{l}</option>)}
            </select>
          ))}
          {(filterCat!=="all"||filterSrc!=="all"||filterUnc!=="all"||search) && (
            <button onClick={()=>{setFilterCat("all");setFilterSrc("all");setFilterUnc("all");setSearch("");reset();}} className="text-xs text-brand-400 hover:text-brand-300">Clear</button>
          )}
          <span className="ml-auto text-xs text-slate-500">{filtered.length} result{filtered.length!==1?"s":""}</span>
        </div>
      </div>

      {paginated.length === 0 ? (
        <div className="glass-card rounded-2xl p-8 text-center"><p className="text-slate-400 text-sm">No results match your filters.</p></div>
      ) : (
        <div className="glass-card rounded-2xl overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-surface-700/50">
                  {["Category","Confidence","Source","Command","Model","Date"].map(h => (
                    <th key={h} className={clsx("text-left text-xs font-semibold text-slate-500 px-4 py-3",
                      ["Source","Command"].includes(h) && "hidden sm:table-cell",
                      ["Model"].includes(h) && "hidden lg:table-cell")}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-surface-700/30">
                {paginated.map(item => (
                  <tr key={item.id} className="hover:bg-surface-700/20 transition-colors">
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <span className={clsx("text-xs px-2 py-0.5 rounded-lg border font-medium", getCategoryBg(item.category))}>
                          {CATEGORY_NAMES[item.category]??item.category}
                        </span>
                        {item.is_uncertain && <AlertTriangle className="w-3 h-3 text-amber-400 shrink-0" />}
                      </div>
                    </td>
                    <td className="px-4 py-3"><span className={clsx("text-xs font-semibold", getConfidenceColor(item.confidence,item.is_uncertain))}>{formatConfidence(item.confidence)}</span></td>
                    <td className="px-4 py-3 hidden sm:table-cell"><span className="text-xs text-slate-400 capitalize">{item.source}</span></td>
                    <td className="px-4 py-3 hidden sm:table-cell"><span className="text-xs font-mono text-slate-500">{item.hardware_command}</span></td>
                    <td className="px-4 py-3 hidden lg:table-cell"><span className="text-xs text-slate-500">{item.model_version}</span></td>
                    <td className="px-4 py-3"><span className="text-xs text-slate-500 whitespace-nowrap">{format(parseISO(item.created_at),"MMM d, HH:mm")}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {totalPages > 1 && (
            <div className="flex items-center justify-between px-5 py-3 border-t border-surface-700/50">
              <button onClick={() => setPage(p => Math.max(1,p-1))} disabled={page===1}
                className="text-xs px-3 py-1.5 rounded-lg bg-surface-700 hover:bg-surface-600 disabled:opacity-40 text-slate-300 transition-colors">Previous</button>
              <span className="text-xs text-slate-500">Page {page} of {totalPages}</span>
              <button onClick={() => setPage(p => Math.min(totalPages,p+1))} disabled={page===totalPages}
                className="text-xs px-3 py-1.5 rounded-lg bg-surface-700 hover:bg-surface-600 disabled:opacity-40 text-slate-300 transition-colors">Next</button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
