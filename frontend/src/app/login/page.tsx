"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Leaf, AlertCircle, Loader2 } from "lucide-react";
import { createClient } from "@/lib/supabase/client";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

async function handleSubmit(e: React.FormEvent) {
  e.preventDefault();

  console.log("🔥 SIGN IN BUTTON CLICKED");

  setError(null);
  setLoading(true);

  try {
    const supabase = createClient();

    console.log("🔥 Calling Supabase...");

    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password,
    });

    console.log("🔥 Supabase response:", { data, error });

    if (error) {
      console.error("❌ LOGIN ERROR:", error);
      setError(error.message);
      return;
    }

    console.log("✅ LOGIN SUCCESS:", data.user);

    window.location.href = "/dashboard";
  } catch (err) {
    console.error("❌ UNEXPECTED ERROR:", err);
    setError("An unexpected error occurred.");
  } finally {
    setLoading(false);
  }
}

  return (
    <div className="min-h-screen bg-surface-900 flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-2 mb-4">
            <div className="p-2 rounded-xl bg-brand-500/10 border border-brand-500/20">
              <Leaf className="w-6 h-6 text-brand-400" />
            </div>
            <span className="text-2xl font-bold text-gradient-green">SmartWaste</span>
          </div>
          <p className="text-slate-400 text-sm">AI-powered waste segregation</p>
        </div>
        <div className="glass-card rounded-2xl p-8">
          <h1 className="text-xl font-semibold text-slate-100 mb-6">Sign in to your account</h1>
          {error && (
            <div className="flex items-start gap-3 p-3 mb-5 bg-red-500/10 border border-red-500/20 rounded-xl">
              <AlertCircle className="w-4 h-4 text-red-400 mt-0.5 shrink-0" />
              <p className="text-sm text-red-400">{error}</p>
            </div>
          )}
          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1.5">Email address</label>
              <input type="email" value={email} onChange={e => setEmail(e.target.value)} required
                placeholder="you@example.com"
                className="w-full px-3.5 py-2.5 rounded-xl bg-surface-700 border border-surface-600 text-slate-100 placeholder-slate-500 text-sm focus:outline-none focus:border-brand-500 transition-colors" />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1.5">Password</label>
              <input type="password" value={password} onChange={e => setPassword(e.target.value)} required
                placeholder="••••••••"
                className="w-full px-3.5 py-2.5 rounded-xl bg-surface-700 border border-surface-600 text-slate-100 placeholder-slate-500 text-sm focus:outline-none focus:border-brand-500 transition-colors" />
            </div>
            <button type="submit" disabled={loading}
              className="w-full flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl bg-brand-500 hover:bg-brand-600 disabled:opacity-50 text-white text-sm font-semibold transition-colors">
              {loading ? <><Loader2 className="w-4 h-4 animate-spin" />Signing in…</> : "Sign in"}
            </button>
          </form>
          <p className="text-center text-sm text-slate-400 mt-6">
            No account?{" "}
            <Link href="/register" className="text-brand-400 hover:text-brand-300 font-medium">Create one</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
