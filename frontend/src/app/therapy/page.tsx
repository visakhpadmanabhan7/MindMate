"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/auth";
import {
  getTherapySessions,
  updateTherapySession,
  createTherapySession,
} from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import {
  Brain,
  ListChecks,
  Lightbulb,
  Wrench,
  Pencil,
  Check,
  X,
  Plus,
  Loader2,
  Save,
} from "lucide-react";

interface TherapySession {
  id: number;
  session_number: number;
  date: string;
  issues_discussed: string[];
  learnings: string;
  action_items: string[];
  techniques: string[];
  created_at: string;
}

export default function TherapyPage() {
  const { email } = useAuth();
  const router = useRouter();
  const [sessions, setSessions] = useState<TherapySession[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editData, setEditData] = useState({
    learnings: "",
    issues: "",
    actions: "",
    techniques: "",
  });

  // New session form
  const [showNewForm, setShowNewForm] = useState(false);
  const [saving, setSaving] = useState(false);
  const [newSession, setNewSession] = useState({
    issues: "",
    learnings: "",
    actions: "",
    techniques: "",
  });

  useEffect(() => {
    if (!email) {
      router.push("/");
      return;
    }
    loadSessions();
  }, [email, router]);

  const loadSessions = () => {
    if (!email) return;
    getTherapySessions(email)
      .then((data) => setSessions(data.sessions))
      .catch((e) => setError(e.message || "Failed to load sessions"))
      .finally(() => setLoading(false));
  };

  const handleCreate = async () => {
    if (!email) return;
    setSaving(true);
    try {
      await createTherapySession(email, {
        issues_discussed: newSession.issues
          .split(",")
          .map((s) => s.trim())
          .filter(Boolean),
        learnings: newSession.learnings,
        action_items: newSession.actions
          .split("\n")
          .map((s) => s.trim())
          .filter(Boolean),
        techniques: newSession.techniques
          .split(",")
          .map((s) => s.trim())
          .filter(Boolean),
      });
      setShowNewForm(false);
      setNewSession({ issues: "", learnings: "", actions: "", techniques: "" });
      loadSessions();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to create session");
    }
    setSaving(false);
  };

  const startEdit = (session: TherapySession) => {
    setEditingId(session.id);
    setEditData({
      learnings: session.learnings,
      issues: session.issues_discussed.join(", "),
      actions: session.action_items.join("\n"),
      techniques: session.techniques.join(", "),
    });
  };

  const handleSave = async (sessionId: number) => {
    if (!email) return;
    try {
      await updateTherapySession(email, sessionId, {
        learnings: editData.learnings,
        issues_discussed: editData.issues
          .split(",")
          .map((s) => s.trim())
          .filter(Boolean),
        action_items: editData.actions
          .split("\n")
          .map((s) => s.trim())
          .filter(Boolean),
        techniques: editData.techniques
          .split(",")
          .map((s) => s.trim())
          .filter(Boolean),
      });
      setEditingId(null);
      loadSessions();
    } catch {
      // ignore
    }
  };

  if (!email) return null;

  return (
    <div className="p-6 pt-20 md:pt-6 space-y-6 max-w-3xl mx-auto">
      <div className="rounded-xl p-6 page-header-gradient flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold">Therapy Sessions</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Log sessions here or in the chat. Ask for session prep or pattern
            analysis.
          </p>
        </div>
        {!showNewForm && (
          <Button
            size="sm"
            onClick={() => setShowNewForm(true)}
            className="gap-1.5 shrink-0"
          >
            <Plus className="h-4 w-4" /> Log Session
          </Button>
        )}
      </div>

      {/* New session form */}
      {showNewForm && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Log a New Session</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="flex items-center gap-2 mb-2 text-sm font-medium">
                <ListChecks className="h-4 w-4" /> Issues Discussed
              </label>
              <Input
                value={newSession.issues}
                onChange={(e) =>
                  setNewSession({ ...newSession, issues: e.target.value })
                }
                placeholder="Comma-separated: anxiety, work stress, relationships"
              />
            </div>
            <div>
              <label className="flex items-center gap-2 mb-2 text-sm font-medium">
                <Lightbulb className="h-4 w-4" /> Learnings
              </label>
              <Textarea
                value={newSession.learnings}
                onChange={(e) =>
                  setNewSession({ ...newSession, learnings: e.target.value })
                }
                placeholder="What did you learn or realize in this session?"
                rows={3}
              />
            </div>
            <div>
              <label className="flex items-center gap-2 mb-2 text-sm font-medium">
                <ListChecks className="h-4 w-4" /> Action Items
              </label>
              <Textarea
                value={newSession.actions}
                onChange={(e) =>
                  setNewSession({ ...newSession, actions: e.target.value })
                }
                placeholder="One per line: Practice breathing daily&#10;Journal before bed"
                rows={3}
              />
            </div>
            <div>
              <label className="flex items-center gap-2 mb-2 text-sm font-medium">
                <Wrench className="h-4 w-4" /> Techniques
              </label>
              <Input
                value={newSession.techniques}
                onChange={(e) =>
                  setNewSession({ ...newSession, techniques: e.target.value })
                }
                placeholder="Comma-separated: CBT, mindfulness, journaling"
              />
            </div>
            <div className="flex justify-end gap-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => {
                  setShowNewForm(false);
                  setNewSession({
                    issues: "",
                    learnings: "",
                    actions: "",
                    techniques: "",
                  });
                }}
              >
                Cancel
              </Button>
              <Button size="sm" onClick={handleCreate} disabled={saving}>
                {saving ? (
                  <Loader2 className="h-4 w-4 mr-1 animate-spin" />
                ) : (
                  <Save className="h-4 w-4 mr-1" />
                )}
                Save Session
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {loading ? (
        <p className="text-muted-foreground">Loading...</p>
      ) : error ? (
        <Card>
          <CardContent className="flex h-48 items-center justify-center text-destructive">
            {error}
          </CardContent>
        </Card>
      ) : sessions.length === 0 ? (
        <Card className="border-dashed">
          <CardContent className="flex flex-col items-center justify-center h-64 text-center">
            <div className="flex h-16 w-16 items-center justify-center rounded-full bg-primary/10 mb-4">
              <Brain className="h-8 w-8 text-primary/60" />
            </div>
            <p className="text-muted-foreground font-medium">
              No therapy sessions recorded yet
            </p>
            <p className="text-sm text-muted-foreground/70 mt-1">
              Share your session notes in the chat to get started
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="relative space-y-0">
          {/* Vertical timeline line */}
          <div className="absolute left-5 top-0 bottom-0 w-px bg-border" />

          {sessions.map((session) => {
            const isEditing = editingId === session.id;

            return (
              <div
                key={session.id}
                className="relative flex gap-4 pb-6 last:pb-0"
              >
                {/* Timeline node */}
                <div className="relative z-10 flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-primary text-primary-foreground text-sm font-bold shadow-sm">
                  {session.session_number}
                </div>

                {/* Card */}
                <Card className="flex-1">
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-base">
                        Session #{session.session_number}
                      </CardTitle>
                      <div className="flex items-center gap-2">
                        <span className="text-sm text-muted-foreground">
                          {session.date}
                        </span>
                        {isEditing ? (
                          <div className="flex gap-1">
                            <Button
                              size="icon"
                              variant="ghost"
                              className="h-7 w-7"
                              onClick={() => handleSave(session.id)}
                            >
                              <Check className="h-4 w-4" />
                            </Button>
                            <Button
                              size="icon"
                              variant="ghost"
                              className="h-7 w-7"
                              onClick={() => setEditingId(null)}
                            >
                              <X className="h-4 w-4" />
                            </Button>
                          </div>
                        ) : (
                          <Button
                            size="icon"
                            variant="ghost"
                            className="h-7 w-7"
                            onClick={() => startEdit(session)}
                          >
                            <Pencil className="h-4 w-4" />
                          </Button>
                        )}
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {/* Issues */}
                    <div>
                      <div className="flex items-center gap-2 mb-2 text-sm font-medium">
                        <ListChecks className="h-4 w-4" /> Issues Discussed
                      </div>
                      {isEditing ? (
                        <Input
                          value={editData.issues}
                          onChange={(e) =>
                            setEditData({
                              ...editData,
                              issues: e.target.value,
                            })
                          }
                          placeholder="Comma-separated issues"
                        />
                      ) : session.issues_discussed.length > 0 ? (
                        <div className="flex flex-wrap gap-1">
                          {session.issues_discussed.map((issue, i) => (
                            <Badge key={i} variant="secondary">
                              {issue}
                            </Badge>
                          ))}
                        </div>
                      ) : (
                        <p className="text-sm text-muted-foreground">—</p>
                      )}
                    </div>

                    {/* Learnings */}
                    <div>
                      <div className="flex items-center gap-2 mb-2 text-sm font-medium">
                        <Lightbulb className="h-4 w-4" /> Learnings
                      </div>
                      {isEditing ? (
                        <Textarea
                          value={editData.learnings}
                          onChange={(e) =>
                            setEditData({
                              ...editData,
                              learnings: e.target.value,
                            })
                          }
                          rows={3}
                        />
                      ) : session.learnings ? (
                        <p className="text-sm text-muted-foreground whitespace-pre-wrap">
                          {session.learnings}
                        </p>
                      ) : (
                        <p className="text-sm text-muted-foreground">—</p>
                      )}
                    </div>

                    {/* Action Items */}
                    <div>
                      <div className="flex items-center gap-2 mb-2 text-sm font-medium">
                        <ListChecks className="h-4 w-4" /> Action Items
                      </div>
                      {isEditing ? (
                        <Textarea
                          value={editData.actions}
                          onChange={(e) =>
                            setEditData({
                              ...editData,
                              actions: e.target.value,
                            })
                          }
                          placeholder="One per line"
                          rows={3}
                        />
                      ) : session.action_items.length > 0 ? (
                        <ul className="space-y-2">
                          {session.action_items.map((item, i) => (
                            <li
                              key={i}
                              className="flex items-start gap-2 text-sm"
                            >
                              <div className="mt-1.5 h-2 w-2 shrink-0 rounded-full bg-primary" />
                              <span className="text-muted-foreground">
                                {item}
                              </span>
                            </li>
                          ))}
                        </ul>
                      ) : (
                        <p className="text-sm text-muted-foreground">—</p>
                      )}
                    </div>

                    {/* Techniques */}
                    <div>
                      <div className="flex items-center gap-2 mb-2 text-sm font-medium">
                        <Wrench className="h-4 w-4" /> Techniques
                      </div>
                      {isEditing ? (
                        <Input
                          value={editData.techniques}
                          onChange={(e) =>
                            setEditData({
                              ...editData,
                              techniques: e.target.value,
                            })
                          }
                          placeholder="Comma-separated techniques"
                        />
                      ) : session.techniques.length > 0 ? (
                        <div className="flex flex-wrap gap-1">
                          {session.techniques.map((tech, i) => (
                            <Badge key={i} variant="outline">
                              {tech}
                            </Badge>
                          ))}
                        </div>
                      ) : (
                        <p className="text-sm text-muted-foreground">—</p>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
