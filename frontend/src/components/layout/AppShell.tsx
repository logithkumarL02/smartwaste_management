"use client";
import { useState } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { Leaf, LayoutDashboard, ScanLine, History, User, LogOut, Menu, ChevronRight } from "lucide-react";
import { createClient } from "@/lib/supabase/client";
import clsx from "clsx";

const NAV = [
  { href: "/dashboard", label: "Dashboard",  Icon: LayoutDashboard },
  { href: "/classify",  label: "Classify",   Icon: ScanLine },
  { href: "/history",   label: "History",    Icon: History },
  { href: "/profile",   label: "Profile",    Icon: User },
];

export default function AppShell({ children, user }: { children: React.ReactNode; user: any }) {
  const pathname = usePathname();
  const router = useRouter();
  const [open, setOpen] = useState(false);

  async function logout() {
    await createClient().auth.signOut();
    router.push("/login"); router.refresh();
  }

  function NavContent() {
    return (
      <div className="flex flex-col h-full">
        <div className="flex items-center gap-2.5 px-5 py-5 border-b border-surface-700/50">
          <div className="p-1.5 rounded-lg bg-brand-500/10 border border-brand-500/20">
            <Leaf className="w-5 h-5 text-brand-400" />
          </div>
          <div>
            <div className="text-sm font-bold text-gradient-green leading-none">SmartWaste</div>
            <div className="text-[10px] text-slate-500 mt-0.5">AI Segregation</div>
          </div>
        </div>
        <nav className="flex-1 px-3 py-4 space-y-1">
          {NAV.map(({ href, label, Icon }) => {
            const active = pathname === href || pathname.startsWith(href + "/");
            return (
              <Link key={href} href={href} onClick={() => setOpen(false)}
                className={clsx("flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all",
                  active ? "bg-brand-500/15 text-brand-400 border border-brand-500/20"
                         : "text-slate-400 hover:text-slate-200 hover:bg-surface-700/50")}>
                <Icon className="w-4 h-4 shrink-0" />{label}
                {active && <ChevronRight className="w-3 h-3 ml-auto" />}
              </Link>
            );
          })}
        </nav>
        <div className="px-3 py-4 border-t border-surface-700/50">
          <div className="flex items-center gap-3 px-3 py-2 mb-2 rounded-xl bg-surface-700/30">
            <div className="w-7 h-7 rounded-full bg-brand-500/20 flex items-center justify-center">
              <span className="text-xs font-semibold text-brand-400">{user?.email?.[0]?.toUpperCase() ?? "?"}</span>
            </div>
            <p className="text-xs font-medium text-slate-200 truncate flex-1">{user?.email}</p>
          </div>
          <button onClick={logout}
            className="flex items-center gap-3 w-full px-3 py-2.5 rounded-xl text-sm text-slate-400 hover:text-red-400 hover:bg-red-500/10 transition-all">
            <LogOut className="w-4 h-4" />Sign out
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen overflow-hidden">
      <aside className="hidden lg:flex w-56 xl:w-60 flex-col bg-surface-800/80 border-r border-surface-700/50 shrink-0">
        <NavContent />
      </aside>
      {open && (
        <div className="lg:hidden fixed inset-0 z-50 flex">
          <div className="fixed inset-0 bg-black/60" onClick={() => setOpen(false)} />
          <aside className="relative w-64 bg-surface-800 border-r border-surface-700/50 z-10 flex flex-col"><NavContent /></aside>
        </div>
      )}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <header className="lg:hidden flex items-center gap-3 px-4 py-3 border-b border-surface-700/50 bg-surface-800/80">
          <button onClick={() => setOpen(true)} className="p-1.5 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-surface-700 transition-colors">
            <Menu className="w-5 h-5" />
          </button>
          <div className="flex items-center gap-2">
            <Leaf className="w-4 h-4 text-brand-400" />
            <span className="text-sm font-bold text-gradient-green">SmartWaste</span>
          </div>
        </header>
        <main className="flex-1 overflow-y-auto">
          <div className="max-w-6xl mx-auto px-4 md:px-6 lg:px-8 py-6 md:py-8">{children}</div>
        </main>
      </div>
    </div>
  );
}
