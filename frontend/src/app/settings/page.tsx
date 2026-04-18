"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/auth";
import { getExportUrl } from "@/lib/api";
import { useToast } from "@/components/ui/toast";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import {
  Download,
  LogOut,
  Shield,
  Heart,
  Cpu,
  BookOpen,
  BarChart3,
  Brain,
} from "lucide-react";

export default function SettingsPage() {
  const { email, logout } = useAuth();
  const router = useRouter();
  const { toast } = useToast();

  useEffect(() => {
    if (!email) router.push("/");
  }, [email, router]);

  if (!email) return null;

  const initials = email.slice(0, 2).toUpperCase();

  const handleExport = () => {
    window.open(getExportUrl(email), "_blank");
    toast("Download started", "info");
  };

  const handleLogout = () => { logout(); router.push("/"); };

  const techStack = [
    { name: "Next.js", desc: "Frontend" },
    { name: "FastAPI", desc: "Backend" },
    { name: "LangGraph", desc: "Agent orchestration" },
    { name: "Groq", desc: "LLM (Llama 3.3 70B)" },
    { name: "ChromaDB", desc: "Vector search" },
    { name: "sentence-transformers", desc: "Embeddings" },
  ];

  return (
    <div className="p-6 pt-20 md:pt-6 max-w-2xl mx-auto space-y-8">
      <div>
        <h1 className="text-2xl font-bold">Settings</h1>
        <p className="text-sm text-muted-foreground mt-1">Manage your account, data, and knowledge base</p>
      </div>

      {/* Profile */}
      <div className="rounded-xl border bg-card p-6">
        <div className="flex items-center gap-4">
          <Avatar className="h-14 w-14">
            <AvatarFallback className="text-lg bg-primary/10 text-primary font-semibold">{initials}</AvatarFallback>
          </Avatar>
          <div className="flex-1 min-w-0">
            <p className="font-medium truncate">{email}</p>
            <div className="flex items-center gap-1.5 mt-1">
              <div className="h-2 w-2 rounded-full bg-green-500" />
              <span className="text-xs text-muted-foreground">Active account</span>
            </div>
          </div>
          <Button variant="outline" size="sm" onClick={handleLogout} className="gap-2 text-muted-foreground hover:text-destructive hover:border-destructive/50">
            <LogOut className="h-4 w-4" /> Logout
          </Button>
        </div>
      </div>

      {/* Data & Privacy */}
      <div>
        <h2 className="text-sm font-medium text-muted-foreground mb-3 uppercase tracking-wider">Data & Privacy</h2>
        <div className="grid gap-3 sm:grid-cols-2">
          <button onClick={handleExport} className="flex items-start gap-3 rounded-xl border bg-card p-4 text-left transition-colors hover:bg-accent group">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-blue-500/10 text-blue-600">
              <Download className="h-5 w-5" />
            </div>
            <div>
              <p className="font-medium text-sm">Export Data</p>
              <p className="text-xs text-muted-foreground mt-0.5">Download all your data as JSON</p>
            </div>
          </button>
          <div className="flex items-start gap-3 rounded-xl border bg-card p-4">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-green-500/10 text-green-600">
              <Shield className="h-5 w-5" />
            </div>
            <div>
              <p className="font-medium text-sm">Privacy</p>
              <p className="text-xs text-muted-foreground mt-0.5">All data stored locally on your machine</p>
            </div>
          </div>
        </div>
      </div>

      {/* What MindMate tracks */}
      <div>
        <h2 className="text-sm font-medium text-muted-foreground mb-3 uppercase tracking-wider">What MindMate Tracks</h2>
        <div className="rounded-xl border bg-card divide-y">
          {[
            { icon: BarChart3, label: "Mood", desc: "Auto-detected from chat and journal entries", color: "text-violet-600 bg-violet-500/10" },
            { icon: BookOpen, label: "Journal entries", desc: "With themes, entities, and mood analysis", color: "text-amber-600 bg-amber-500/10" },
            { icon: Brain, label: "Therapy sessions", desc: "Structured notes with pattern tracking", color: "text-pink-600 bg-pink-500/10" },
            { icon: Heart, label: "Wellbeing insights", desc: "Cross-referenced with CBT science", color: "text-red-600 bg-red-500/10" },
          ].map(({ icon: Icon, label, desc, color }) => (
            <div key={label} className="flex items-center gap-3 p-4">
              <div className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-lg ${color}`}>
                <Icon className="h-4 w-4" />
              </div>
              <div>
                <p className="text-sm font-medium">{label}</p>
                <p className="text-xs text-muted-foreground">{desc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Tech Stack */}
      <div>
        <h2 className="text-sm font-medium text-muted-foreground mb-3 uppercase tracking-wider">Tech Stack</h2>
        <div className="rounded-xl border bg-card p-4">
          <div className="flex flex-wrap gap-2">
            {techStack.map(({ name, desc }) => (
              <div key={name} className="inline-flex items-center gap-1.5 rounded-full border px-3 py-1.5 text-xs">
                <Cpu className="h-3 w-3 text-muted-foreground" />
                <span className="font-medium">{name}</span>
                <span className="text-muted-foreground">- {desc}</span>
              </div>
            ))}
          </div>
          <Separator className="my-3" />
          <p className="text-xs text-muted-foreground text-center">100% free and open-source stack.</p>
        </div>
      </div>

      {/* Disclaimer */}
      <div className="rounded-xl border border-amber-200 bg-amber-50 p-4 text-center">
        <p className="text-xs text-amber-800">
          MindMate is not a substitute for professional mental health support. If you are in crisis, please contact the 988 Suicide & Crisis Lifeline.
        </p>
      </div>
    </div>
  );
}
