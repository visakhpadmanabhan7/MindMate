"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/auth";
import { getMoodAnalytics, getMoodDetail } from "@/lib/api";
import { getMoodColor } from "@/lib/utils";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { MoodDetailPanel } from "@/components/mood-detail-panel";
import {
  Activity,
  Flame,
  Hash,
  MessageCircle,
  BookOpen,
  Target,
} from "lucide-react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Area,
  AreaChart,
} from "recharts";

const moodValues: Record<string, number> = {
  happy: 5,
  grateful: 5,
  hopeful: 4,
  calm: 4,
  tired: 3,
  stressed: 3,
  numb: 2,
  sad: 2,
  lonely: 2,
  anxious: 1,
  angry: 1,
  overwhelmed: 1,
};

interface MoodTimeline {
  id: number;
  date: string;
  mood: string;
  message: string;
  source_type: string;
  source_id: number | null;
  timestamp: string;
}

interface MoodData {
  timeline: MoodTimeline[];
  distribution: Record<string, number>;
  total_entries: number;
  streak: number;
  sources: Record<string, number>;
}

interface MoodDetail {
  id: number;
  mood: string;
  message: string;
  timestamp: string;
  source_type: string;
  source_id: number | null;
  source_content: string | null;
}

export default function DashboardPage() {
  const { email } = useAuth();
  const router = useRouter();
  const [data, setData] = useState<MoodData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [selectedDetail, setSelectedDetail] = useState<MoodDetail | null>(null);

  useEffect(() => {
    if (!email) {
      router.push("/");
      return;
    }
    getMoodAnalytics(email)
      .then(setData)
      .catch((e) => setError(e.message || "Failed to load mood data"));
  }, [email, router]);

  const handleDotClick = async (entry: MoodTimeline) => {
    if (!email) return;
    try {
      const detail = await getMoodDetail(email, entry.id);
      setSelectedDetail(detail);
    } catch {
      setSelectedDetail({
        id: entry.id,
        mood: entry.mood,
        message: entry.message,
        timestamp: entry.timestamp,
        source_type: entry.source_type,
        source_id: entry.source_id,
        source_content: null,
      });
    }
  };

  if (!email) return null;

  if (error) {
    return (
      <div className="p-6 pt-20 md:pt-6">
        <div className="rounded-xl p-6 page-header-gradient mb-6">
          <h1 className="text-2xl font-bold">Mood Dashboard</h1>
        </div>
        <Card>
          <CardContent className="flex h-48 items-center justify-center text-destructive">
            {error}
          </CardContent>
        </Card>
      </div>
    );
  }

  const pieData = data
    ? Object.entries(data.distribution).map(([name, value]) => ({
        name,
        value,
      }))
    : [];

  const timelineData =
    data?.timeline.map((entry) => ({
      ...entry,
      value: moodValues[entry.mood] ?? 3,
    })) ?? [];

  const totalSources = data?.sources
    ? Object.values(data.sources).reduce((a, b) => a + b, 0) || 1
    : 1;

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const CustomTooltip = ({ active, payload }: any) => {
    if (!active || !payload?.length) return null;
    const entry = payload[0].payload;
    return (
      <div className="rounded-lg border bg-card p-3 shadow-lg text-sm">
        <p
          className="font-medium capitalize"
          style={{ color: getMoodColor(entry.mood) }}
        >
          {entry.mood}
        </p>
        <p className="text-xs text-muted-foreground mt-1">{entry.date}</p>
        {entry.message && (
          <p className="text-xs mt-1 max-w-48 truncate">{entry.message}</p>
        )}
      </div>
    );
  };

  return (
    <div className="p-6 pt-20 md:pt-6 space-y-6">
      <div className="rounded-xl p-6 page-header-gradient">
        <h1 className="text-2xl font-bold">Mood Dashboard</h1>
        <p className="text-sm text-muted-foreground mt-1">
          Track your emotional patterns over time
        </p>
      </div>

      {!data || data.total_entries === 0 ? (
        <Card className="border-dashed">
          <CardContent className="flex flex-col items-center justify-center h-64 text-center">
            <div className="flex h-16 w-16 items-center justify-center rounded-full bg-primary/10 mb-4">
              <Activity className="h-8 w-8 text-primary/60" />
            </div>
            <p className="text-muted-foreground font-medium">
              No mood data yet
            </p>
            <p className="text-sm text-muted-foreground/70 mt-1">
              Start chatting or journaling to track your moods!
            </p>
          </CardContent>
        </Card>
      ) : (
        <>
          {/* Stats cards */}
          <div className="grid gap-4 grid-cols-2 md:grid-cols-4">
            <Card className="relative overflow-hidden">
              <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent pointer-events-none" />
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium">
                  Total Entries
                </CardTitle>
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10">
                  <Hash className="h-4 w-4 text-primary" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{data.total_entries}</div>
              </CardContent>
            </Card>

            <Card className="relative overflow-hidden">
              <div className="absolute inset-0 bg-gradient-to-br from-amber-500/5 to-transparent pointer-events-none" />
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium">Streak</CardTitle>
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-amber-500/10">
                  <Flame className="h-4 w-4 text-amber-600" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{data.streak} days</div>
              </CardContent>
            </Card>

            <Card className="relative overflow-hidden">
              <div className="absolute inset-0 bg-gradient-to-br from-violet-500/5 to-transparent pointer-events-none" />
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium">
                  Most Common
                </CardTitle>
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-violet-500/10">
                  <Activity className="h-4 w-4 text-violet-600" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold capitalize">
                  {pieData.sort((a, b) => b.value - a.value)[0]?.name ?? "—"}
                </div>
              </CardContent>
            </Card>

            <Card className="relative overflow-hidden">
              <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 to-transparent pointer-events-none" />
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium">Sources</CardTitle>
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-500/10">
                  <MessageCircle className="h-4 w-4 text-blue-600" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="flex gap-3 text-xs flex-wrap">
                  {(data.sources?.chat ?? 0) > 0 && (
                    <span className="flex items-center gap-1">
                      <MessageCircle className="h-3 w-3" />
                      Chat{" "}
                      {Math.round(
                        ((data.sources.chat ?? 0) / totalSources) * 100
                      )}
                      %
                    </span>
                  )}
                  {(data.sources?.journal ?? 0) > 0 && (
                    <span className="flex items-center gap-1">
                      <BookOpen className="h-3 w-3" />
                      Journal{" "}
                      {Math.round(
                        ((data.sources.journal ?? 0) / totalSources) * 100
                      )}
                      %
                    </span>
                  )}
                  {(data.sources?.explicit ?? 0) > 0 && (
                    <span className="flex items-center gap-1">
                      <Target className="h-3 w-3" />
                      Explicit{" "}
                      {Math.round(
                        ((data.sources.explicit ?? 0) / totalSources) * 100
                      )}
                      %
                    </span>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Charts */}
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle className="text-sm font-medium">
                  Mood Over Time
                  <span className="text-xs text-muted-foreground font-normal ml-2">
                    (click a point for details)
                  </span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto min-w-0">
                  <ResponsiveContainer width="100%" height={250}>
                    <AreaChart data={timelineData}>
                      <defs>
                        <linearGradient
                          id="moodGradient"
                          x1="0"
                          y1="0"
                          x2="0"
                          y2="1"
                        >
                          <stop
                            offset="0%"
                            stopColor="oklch(0.45 0.08 155)"
                            stopOpacity={0.3}
                          />
                          <stop
                            offset="100%"
                            stopColor="oklch(0.45 0.08 155)"
                            stopOpacity={0}
                          />
                        </linearGradient>
                      </defs>
                      <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                      <YAxis
                        domain={[0, 6]}
                        ticks={[1, 2, 3, 4, 5]}
                        tickFormatter={(v) =>
                          ["", "Low", "Down", "Neutral", "Good", "Great"][v] ??
                          ""
                        }
                        tick={{ fontSize: 11 }}
                      />
                      <Tooltip content={<CustomTooltip />} />
                      <Area
                        type="monotone"
                        dataKey="value"
                        stroke="oklch(0.45 0.08 155)"
                        strokeWidth={2}
                        fill="url(#moodGradient)"
                        dot={(props) => {
                          const { cx, cy, payload } = props;
                          const color = getMoodColor(payload.mood);
                          return (
                            <circle
                              key={`dot-${payload.id}`}
                              cx={cx}
                              cy={cy}
                              r={5}
                              fill={color}
                              stroke="white"
                              strokeWidth={2}
                              className="cursor-pointer drop-shadow-sm"
                            />
                          );
                        }}
                        activeDot={{
                          r: 7,
                          // eslint-disable-next-line @typescript-eslint/no-explicit-any
                          onClick: (_: any, payload: any) => {
                            if (payload?.payload) handleDotClick(payload.payload);
                          },
                        }}
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-sm font-medium">
                  Mood Distribution
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={250}>
                  <PieChart>
                    <Pie
                      data={pieData}
                      dataKey="value"
                      nameKey="name"
                      cx="50%"
                      cy="50%"
                      outerRadius={90}
                      label={({ name, percent }) =>
                        `${name} ${((percent ?? 0) * 100).toFixed(0)}%`
                      }
                    >
                      {pieData.map((entry, i) => (
                        <Cell key={i} fill={getMoodColor(entry.name)} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>

          {/* Detail Panel */}
          {selectedDetail && (
            <MoodDetailPanel
              detail={selectedDetail}
              onClose={() => setSelectedDetail(null)}
            />
          )}

          {/* Recent Moods */}
          <Card>
            <CardHeader>
              <CardTitle className="text-sm font-medium">
                Recent Moods
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2">
                {data.timeline
                  .slice(-20)
                  .reverse()
                  .map((entry) => (
                    <Badge
                      key={entry.id}
                      className="capitalize cursor-pointer text-white"
                      style={{ backgroundColor: getMoodColor(entry.mood) }}
                      onClick={() => handleDotClick(entry)}
                    >
                      {entry.mood} — {entry.date}
                    </Badge>
                  ))}
              </div>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}
