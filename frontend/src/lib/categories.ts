export const CATEGORY_COLORS: Record<string, string> = {
  plastic:"#3B82F6", metal:"#6B7280", glass:"#10B981", paper_cardboard:"#F59E0B",
  organic:"#84CC16", e_waste:"#EF4444", textile:"#8B5CF6", other:"#9CA3AF", unknown:"#D1D5DB",
};

export const CATEGORY_BG: Record<string, string> = {
  plastic:"bg-blue-500/10 text-blue-400 border-blue-500/20",
  metal:"bg-gray-500/10 text-gray-300 border-gray-500/20",
  glass:"bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
  paper_cardboard:"bg-amber-500/10 text-amber-400 border-amber-500/20",
  organic:"bg-lime-500/10 text-lime-400 border-lime-500/20",
  e_waste:"bg-red-500/10 text-red-400 border-red-500/20",
  textile:"bg-violet-500/10 text-violet-400 border-violet-500/20",
  other:"bg-slate-500/10 text-slate-300 border-slate-500/20",
  unknown:"bg-slate-700/30 text-slate-400 border-slate-600/20",
};

export const CATEGORY_NAMES: Record<string, string> = {
  plastic:"Plastic", metal:"Metal", glass:"Glass", paper_cardboard:"Paper & Cardboard",
  organic:"Organic", e_waste:"E-Waste", textile:"Textile", other:"General Waste", unknown:"Unknown",
};

export const getCategoryColor = (c: string) => CATEGORY_COLORS[c] ?? CATEGORY_COLORS.other;
export const getCategoryName = (c: string) => CATEGORY_NAMES[c] ?? c;
export const getCategoryBg = (c: string) => CATEGORY_BG[c] ?? CATEGORY_BG.other;
export const getConfidenceColor = (conf: number, uncertain: boolean) => {
  if (uncertain) return "text-amber-400";
  if (conf >= 0.8) return "text-emerald-400";
  if (conf >= 0.6) return "text-yellow-400";
  return "text-red-400";
};
export const formatConfidence = (conf: number) => `${(conf * 100).toFixed(1)}%`;
