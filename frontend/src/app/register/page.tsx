"use client";
import { useState } from "react";
import Link from "next/link";
import { Leaf, AlertCircle, CheckCircle, Loader2 } from "lucide-react";
import { createClient } from "@/lib/supabase/client";

export default function RegisterPage() {
  const [displayName, setDisplayName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault(); setError(null);
    if (displayName.trim().length < 2) return setError("Display name must be at least 2 characters.");
    if (password.length < 6) return setError("Password must be at least 6 characters.");
    if (password !== confirm) return setError("Passwords do not match.");
    setLoading(true);
    try {
      const { error } = await createClient().auth.signUp({
        email, password, options: { data: { display_name: displayName.trim() } },
      });
      if (error) setError(error.message);
      else setSuccess(true);
    } catch { setError("An unexpected error occurred."); }
    finally { setLoading(false); }
  }

  if (success) return (
    <div className="min-h-screen bg-surface-900 flex items-center justify-center px-4">
      <div className="w-full max-w-md glass-card rounded-2xl p-8 text-center">
        <CheckCircle className="w-12 h-12 text-brand-400 mx-auto mb-4" />
        <h2 className="text-xl font-semibold text-slate-100 mb-2">Check your email</h2>
        <p className="text-slate-400 text-sm mb-6">We sent a confirmation link to <strong className="text-slate-200">{email}</strong>.</p>
        <Link href="/login" className="inline-flex items-center gap-2 py-2.5 px-5 rounded-xl bg-brand-500 hover:bg-brand-600 text-white text-sm font-semibold transition-colors">Back to sign in</Link>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-surface-900 flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-2 mb-4">
            <div className="p-2 rounded-xl bg-brand-500/10 border border-brand-500/20"><Leaf className="w-6 h-6 text-brand-400" /></div>
            <span className="text-2xl font-bold text-gradient-green">SmartWaste</span>
          </div>
          <p className="text-slate-400 text-sm">Create your account</p>
        </div>
        <div className="glass-card rounded-2xl p-8">
          <h1 className="text-xl font-semibold text-slate-100 mb-6">Get started</h1>
          {error && (
            <div className="flex items-start gap-3 p-3 mb-5 bg-red-500/10 border border-red-500/20 rounded-xl">
              <AlertCircle className="w-4 h-4 text-red-400 mt-0.5 shrink-0" /><p className="text-sm text-red-400">{error}</p>
            </div>
          )}
          <form onSubmit={handleSubmit} className="space-y-4">
            {[
              { label:"Display name", type:"text", val:displayName, set:setDisplayName, ph:"Your name" },
              { label:"Email address", type:"email", val:email, set:setEmail, ph:"you@example.com" },
              { label:"Password", type:"password", val:password, set:setPassword, ph:"Min. 6 characters" },
              { label:"Confirm password", type:"password", val:confirm, set:setConfirm, ph:"••••••••" },
            ].map(({ label, type, val, set, ph }) => (
              <div key={label}>
                <label className="block text-sm font-medium text-slate-300 mb-1.5">{label}</label>
                <input type={type} value={val} onChange={e => set(e.target.value)} required placeholder={ph}
                  className="w-full px-3.5 py-2.5 rounded-xl bg-surface-700 border border-surface-600 text-slate-100 placeholder-slate-500 text-sm focus:outline-none focus:border-brand-500 transition-colors" />
              </div>
            ))}
            <button type="submit" disabled={loading}
              className="w-full flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl bg-brand-500 hover:bg-brand-600 disabled:opacity-50 text-white text-sm font-semibold transition-colors mt-2">
              {loading ? <><Loader2 className="w-4 h-4 animate-spin" />Creating account…</> : "Create account"}
            </button>
          </form>
          <p className="text-center text-sm text-slate-400 mt-6">
            Already have an account?{" "}
            <Link href="/login" className="text-brand-400 hover:text-brand-300 font-medium">Sign in</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
