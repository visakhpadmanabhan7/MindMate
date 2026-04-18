"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/auth";
import { getWeeklySummary } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  CalendarDays,
  BarChart3,
  BookOpen,
  Brain,
  Loader2,
  RefreshCw,
} from "lucide-react";
import { Markdown } from "@/components/markdown";

interface SummaryData {
  period: string;
  summary: string;
  stats: {
    mood_entries: number;
    journal_entries: number;
    therapy_sessions: number;
  };
  generated_at: string;
}

export default function SummaryPage() {
  const { email } = useAuth();
  const router = useRouter();
  const [data, setData] = useState<SummaryData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!email) {
      router.push("/");
      return;
    }
    loadSummary();
  }, [email, router]);

  const loadSummary = async () => {
    if (!email) return;
    setLoading(true);
    setError(null);
    try {
      const result = await getWeeklySummary(email);
      setData(result);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load summary");
    }
    setLoading(false);
  };

  if (!email) return null;

  return (
    <div className="p-6 pt-20 md:pt-6 space-y-6 max-w-3xl mx-auto">
      <div className="rounded-xl p-6 page-header-gradient flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold">Weekly Summary</h1>
          {data && (
            <p className="text-sm text-muted-foreground mt-1">{data.period}</p>
          )}
        </div>
        <Button
          size="sm"
          variant="outline"
          onClick={loadSummary}
          disabled={loading}
          className="gap-1.5 shrink-0"
        >
          {loading ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <RefreshCw className="h-4 w-4" />
          )}
          Regenerate
        </Button>
      </div>

      {loading ? (
        <div className="flex justify-center py-16">
          <div className="text-center space-y-3">
            <Loader2 className="h-8 w-8 animate-spin text-primary mx-auto" />
            <p className="text-sm text-muted-foreground">
              Analyzing your week...
            </p>
          </div>
        </div>
      ) : error ? (
        <Card>
          <CardContent className="flex h-48 items-center justify-center text-destructive">
            {error}
          </CardContent>
        </Card>
      ) : data ? (
        <>
          {/* Stats row */}
          <div className="grid grid-cols-3 gap-3">
            <Card className="relative overflow-hidden">
              <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent pointer-events-none" />
              <CardContent className="p-4 text-center">
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10 mx-auto mb-2">
                  <BarChart3 className="h-4 w-4 text-primary" />
                </div>
                <p className="text-2xl font-bold">{data.stats.mood_entries}</p>
                <p className="text-xs text-muted-foreground">Mood Entries</p>
              </CardContent>
            </Card>
            <Card className="relative overflow-hidden">
              <div className="absolute inset-0 bg-gradient-to-br from-amber-500/5 to-transparent pointer-events-none" />
              <CardContent className="p-4 text-center">
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-amber-500/10 mx-auto mb-2">
                  <BookOpen className="h-4 w-4 text-amber-600" />
                </div>
                <p className="text-2xl font-bold">
                  {data.stats.journal_entries}
                </p>
                <p className="text-xs text-muted-foreground">Journal Entries</p>
              </CardContent>
            </Card>
            <Card className="relative overflow-hidden">
              <div className="absolute inset-0 bg-gradient-to-br from-violet-500/5 to-transparent pointer-events-none" />
              <CardContent className="p-4 text-center">
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-violet-500/10 mx-auto mb-2">
                  <Brain className="h-4 w-4 text-violet-600" />
                </div>
                <p className="text-2xl font-bold">
                  {data.stats.therapy_sessions}
                </p>
                <p className="text-xs text-muted-foreground">
                  Therapy Sessions
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Summary content */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <CalendarDays className="h-4 w-4 text-primary" />
                Your Week in Review
              </CardTitle>
            </CardHeader>
            <CardContent>
              <Markdown content={data.summary} />
            </CardContent>
          </Card>

          <p className="text-[10px] text-muted-foreground/50 text-center">
            Generated{" "}
            {new Date(data.generated_at).toLocaleString("en-US", {
              dateStyle: "medium",
              timeStyle: "short",
            })}
          </p>
        </>
      ) : null}
    </div>
  );
}
