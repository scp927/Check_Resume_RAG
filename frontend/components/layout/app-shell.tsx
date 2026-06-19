"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import type { Route } from "next";
import type { ReactNode } from "react";
import { BarChart3, Briefcase, Building2, Upload, Users, Workflow } from "lucide-react";

import { cn } from "@/lib/utils";

const nav: Array<{ href: Route; label: string; icon: typeof BarChart3 }> = [
  { href: "/dashboard", label: "Dashboard", icon: BarChart3 },
  { href: "/resumes", label: "Resumes", icon: Users },
  { href: "/jobs", label: "Jobs", icon: Briefcase },
  { href: "/ats-run", label: "Screening", icon: Workflow },
  { href: "/upload", label: "Upload", icon: Upload }
];

export function AppShell({ children }: { children: ReactNode }) {
  const pathname = usePathname();

  return (
    <div className="min-h-screen bg-[#f4f6f8] text-slate-950 lg:grid lg:grid-cols-[252px_1fr]">
      <aside className="border-r border-slate-200 bg-white text-slate-950 lg:sticky lg:top-0 lg:h-screen">
        <Link href="/dashboard" className="flex items-center gap-3 border-b border-slate-200 px-5 py-5">
          <div className="flex h-10 w-10 items-center justify-center border border-slate-300 bg-slate-950">
            <Building2 className="h-5 w-5 text-white" />
          </div>
          <div>
            <div className="text-base font-bold tracking-tight">RecruitAI ATS</div>
            <div className="text-xs uppercase tracking-wide text-slate-500">Talent command center</div>
          </div>
        </Link>
        <div className="border-b border-slate-200 px-5 py-3 text-[11px] font-semibold uppercase tracking-widest text-slate-500">
          Recruiting
        </div>
        <nav className="grid">
          {nav.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 border-b border-slate-100 px-5 py-3 text-sm font-medium text-slate-600 transition hover:bg-slate-50 hover:text-slate-950",
                pathname === item.href && "border-l-4 border-l-slate-950 bg-slate-50 pl-4 text-slate-950"
              )}
            >
              <item.icon className="h-4 w-4" />
              {item.label}
            </Link>
          ))}
        </nav>
      </aside>
      <section className="min-w-0">
        <header className="sticky top-0 z-10 border-b border-slate-200 bg-white px-6 py-4 lg:px-8">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <div className="text-sm font-semibold text-slate-950">Recruiting Workspace</div>
              <div className="text-xs text-slate-500">Pipeline, screening, and requisitions</div>
            </div>
          </div>
        </header>
        <main className="mx-auto max-w-7xl p-4 sm:p-6 lg:p-8">{children}</main>
      </section>
    </div>
  );
}
