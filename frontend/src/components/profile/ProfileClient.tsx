"use client";
import { useState } from "react";
import { User, Mail, ScanLine, CheckCircle2, AlertCircle, Loader2 } from "lucide-react";
import { createClient } from "@/lib/supabase/client";

export default function ProfileClient({ user, profile, totalPredictions }: { user: any; profile: any; totalPredictions: number }) {
  const [displayName, setDisplayName] = useState(profile?.display_name ?? "");
  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState<{ type:"success"|"error"; text:string }|null>(null);

  const joined = new Date(user.created_at).toLocaleDateString("en-GB", { year:"numeric", month:"long", day:"numeric" });

  async function save(e: React.FormEvent) {
    e.preventDefault(); setMsg(null);
    if (displayName.trim().length < 2) return setMsg({ type:"error", text:"Display name must be at least 2 characters." });
    setSaving(true);
    try {
      const { error } = await createClient().from("profiles").upsert(
        { user_id: user.id, display_name: displayName.trim(), updated_at: new Date().toISOString() },
        { onConflict: "user_id" }
      );
      if (error) throw error;
      setMsg({ type:"success", text:"Profile updated successfully." });
    } catch (err: any) { setMsg({ type:"error", text: err.message ?? "Update failed." }); }
    finally { setSaving(false); }
  }

  return (
    <div className="animate-fade-in max-w-xl mx-auto space-y-5">
      <div>
        <h1 className="text-2xl font-bold text-slate-100">Profile</h1>
        <p className="text-slate-400 text-sm mt-1">Manage your account details.</p>
      </div>

      <div className="glass-card rounded-2xl p-6 flex items-center gap-5">
        <div className="w-16 h-16 rounded-2xl bg-brand-500/20 border border-brand-500/30 flex items-center justify-center shrink-0">
          <span className="text-2xl font-bold text-brand-400">{(displayName||user.email||"?")[0].toUpperCase()}</span>
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-lg font-semibold text-slate-100 truncate">{displayName||user.email?.split("@")[0]||"—"}</p>
          <p className="text-sm text-slate-400 truncate">{user.email}</p>
          <div className="flex items-center gap-4 mt-2">
            <span className="flex items-center gap-1.5 text-xs text-slate-500"><ScanLine className="w-3.5 h-3.5" />{totalPredictions} classification{totalPredictions!==1?"s":""}</span>
            <span className="text-xs text-slate-500">Joined {joined}</span>
          </div>
        </div>
      </div>

      <div className="glass-card rounded-2xl p-6">
        <h2 className="text-sm font-semibold text-slate-300 mb-4">Edit profile</h2>
        {msg && (
          <div className={`flex items-center gap-2 p-3 mb-4 rounded-xl border text-sm ${msg.type==="success" ? "bg-brand-500/10 border-brand-500/20 text-brand-300" : "bg-red-500/10 border-red-500/20 text-red-400"}`}>
            {msg.type==="success" ? <CheckCircle2 className="w-4 h-4 shrink-0" /> : <AlertCircle className="w-4 h-4 shrink-0" />}
            {msg.text}
          </div>
        )}
        <form onSubmit={save} className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1.5">Display name</label>
            <div className="relative">
              <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
              <input type="text" value={displayName} onChange={e => setDisplayName(e.target.value)} placeholder="Your name"
                className="w-full pl-9 pr-4 py-2.5 rounded-xl bg-surface-700 border border-surface-600 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-brand-500 transition-colors" />
            </div>
          </div>
          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1.5">Email address</label>
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
              <input type="email" value={user.email??""} disabled
                className="w-full pl-9 pr-4 py-2.5 rounded-xl bg-surface-800 border border-surface-700 text-sm text-slate-500 cursor-not-allowed" />
            </div>
            <p className="text-xs text-slate-600 mt-1">Email cannot be changed here.</p>
          </div>
          <button type="submit" disabled={saving}
            className="flex items-center justify-center gap-2 px-5 py-2.5 rounded-xl bg-brand-500 hover:bg-brand-600 disabled:opacity-50 text-white text-sm font-semibold transition-colors">
            {saving ? <><Loader2 className="w-4 h-4 animate-spin" />Saving…</> : "Save changes"}
          </button>
        </form>
      </div>

      <div className="glass-card rounded-2xl p-5">
        <h2 className="text-sm font-semibold text-slate-300 mb-3">Account</h2>
        <div className="space-y-2 text-sm">
          {[["User ID", user.id.slice(0,8)+"…"], ["Provider","Email / Password"], ["Total classifications", String(totalPredictions)]].map(([k,v]) => (
            <div key={k} className="flex justify-between">
              <span className="text-slate-500">{k}</span>
              <span className="text-slate-400 font-mono text-xs">{v}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
