"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/auth";
import { getMoodColor } from "@/lib/utils";
import {
  getJournalEntries,
  createJournalEntry,
  updateJournalEntry,
  deleteJournalEntry,
  getJournalThemes,
} from "@/lib/api";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Search,
  BookOpen,
  Save,
  Pencil,
  X,
  Loader2,
  Calendar,
  Tag,
  User,
  Sparkles,
  Trash2,
} from "lucide-react";

interface JournalEntry {
  id: number;
  content: string;
  mood_label: string | null;
  themes: string[];
  entities: string[];
  created_at: string;
  updated_at: string | null;
}

interface Theme {
  name: string;
  count: number;
}

export default function JournalPage() {
  const { email } = useAuth();
  const router = useRouter();
  const [entries, setEntries] = useState<JournalEntry[]>([]);
  const [themes, setThemes] = useState<Theme[]>([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Editor
  const [editorContent, setEditorContent] = useState("");
  const [editingId, setEditingId] = useState<number | null>(null);
  const [saving, setSaving] = useState(false);
  const [lastSaved, setLastSaved] = useState<{
    mood_label: string;
    themes: string[];
    entities: string[];
  } | null>(null);

  // Detail view
  const [viewEntry, setViewEntry] = useState<JournalEntry | null>(null);
  const [confirmDelete, setConfirmDelete] = useState<number | null>(null);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    if (!email) {
      router.push("/");
      return;
    }
    loadEntries();
    loadThemes();
  }, [email, router]);

  const loadEntries = async (searchTerm?: string) => {
    if (!email) return;
    setLoading(true);
    setError(null);
    try {
      const data = await getJournalEntries(email, 50, 0, searchTerm);
      setEntries(data.entries);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to load entries");
    }
    setLoading(false);
  };

  const loadThemes = async () => {
    if (!email) return;
    try {
      const data = await getJournalThemes(email);
      setThemes(data.themes);
    } catch {}
  };

  const handleSave = async () => {
    if (!email || !editorContent.trim() || saving) return;
    setSaving(true);
    setLastSaved(null);
    try {
      if (editingId) {
        const result = await updateJournalEntry(
          email,
          editingId,
          editorContent
        );
        setLastSaved({
          mood_label: result.mood_label,
          themes: result.themes,
          entities: result.entities,
        });
        setEditingId(null);
      } else {
        const result = await createJournalEntry(email, editorContent);
        setLastSaved({
          mood_label: result.mood_label,
          themes: result.themes,
          entities: result.entities,
        });
      }
      setEditorContent("");
      loadEntries();
      loadThemes();
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to save");
    }
    setSaving(false);
  };

  const handleDelete = async (entryId: number) => {
    if (!email) return;
    setDeleting(true);
    try {
      await deleteJournalEntry(email, entryId);
      setViewEntry(null);
      setConfirmDelete(null);
      loadEntries();
      loadThemes();
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to delete");
    }
    setDeleting(false);
  };

  const startEdit = (entry: JournalEntry) => {
    setEditingId(entry.id);
    setEditorContent(entry.content);
    setLastSaved(null);
    setViewEntry(null);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  if (!email) return null;

  const formatDate = (d: string) =>
    new Date(d).toLocaleDateString("en-US", {
      weekday: "short",
      year: "numeric",
      month: "short",
      day: "numeric",
    });

  const formatDateFull = (d: string) =>
    new Date(d).toLocaleString("en-US", {
      weekday: "long",
      year: "numeric",
      month: "long",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });

  const maxThemeCount = Math.max(...themes.map((t) => t.count), 1);

  return (
    <div className="p-6 pt-20 md:pt-6 space-y-6 max-w-3xl mx-auto">
      <div className="rounded-xl p-6 page-header-gradient">
        <h1 className="text-2xl font-bold">Journal</h1>
        <p className="text-sm text-muted-foreground mt-1">
          Write, reflect, and track your themes
        </p>
      </div>

      {/* Editor */}
      <div className="rounded-xl border bg-card p-5 space-y-4">
        <div className="flex items-center gap-2">
          <Sparkles className="h-4 w-4 text-primary" />
          <span className="text-sm font-medium">
            {editingId ? `Editing entry` : "New Entry"}
          </span>
        </div>
        <Textarea
          placeholder="What's on your mind? Write freely — mood, themes, and entities will be detected automatically..."
          value={editorContent}
          onChange={(e) => setEditorContent(e.target.value)}
          className="min-h-[140px] resize-y border-0 bg-muted/50 focus-visible:ring-1 rounded-lg p-4 text-sm leading-relaxed"
          rows={6}
        />
        <div className="flex items-center justify-between">
          <span className="text-xs text-muted-foreground">
            {editorContent.length} characters
          </span>
          <div className="flex gap-2">
            {editingId && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => {
                  setEditingId(null);
                  setEditorContent("");
                  setLastSaved(null);
                }}
              >
                <X className="h-4 w-4 mr-1" /> Cancel
              </Button>
            )}
            <Button
              size="sm"
              onClick={handleSave}
              disabled={!editorContent.trim() || saving}
            >
              {saving ? (
                <Loader2 className="h-4 w-4 mr-1 animate-spin" />
              ) : (
                <Save className="h-4 w-4 mr-1" />
              )}
              {editingId ? "Update" : "Save"}
            </Button>
          </div>
        </div>

        {lastSaved && (
          <div className="rounded-lg bg-primary/5 border border-primary/10 p-3 space-y-2">
            <p className="text-xs font-medium text-primary">
              Auto-detected analysis:
            </p>
            <div className="flex flex-wrap gap-2">
              <Badge className="capitalize">{lastSaved.mood_label}</Badge>
              {lastSaved.themes.map((t, i) => (
                <Badge key={i} variant="outline" className="text-xs">
                  <Tag className="h-3 w-3 mr-1" />
                  {t}
                </Badge>
              ))}
              {lastSaved.entities.map((e, i) => (
                <Badge key={i} variant="secondary" className="text-xs">
                  <User className="h-3 w-3 mr-1" />
                  {e}
                </Badge>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Theme Cloud */}
      {themes.length > 0 && (
        <div>
          <h2 className="text-sm font-medium text-muted-foreground mb-2 uppercase tracking-wider">
            Your Themes
          </h2>
          <div className="flex flex-wrap gap-2">
            {themes.map((t) => {
              const weight = t.count / maxThemeCount;
              const fontSize = 0.7 + weight * 0.5;
              return (
                <Badge
                  key={t.name}
                  variant={search === t.name ? "default" : "outline"}
                  className="cursor-pointer transition-all"
                  style={{
                    fontSize: `${fontSize}rem`,
                    padding: `${0.2 + weight * 0.15}rem ${0.4 + weight * 0.2}rem`,
                  }}
                  onClick={() => {
                    if (search === t.name) {
                      setSearch("");
                      loadEntries();
                    } else {
                      setSearch(t.name);
                      loadEntries(t.name);
                    }
                  }}
                >
                  {t.name}{" "}
                  <span className="ml-1 opacity-60">({t.count})</span>
                </Badge>
              );
            })}
          </div>
        </div>
      )}

      {/* Search */}
      <div className="flex gap-2">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search entries..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            onKeyDown={(e) =>
              e.key === "Enter" && loadEntries(search || undefined)
            }
            className="pl-9"
          />
        </div>
        <Button
          variant="outline"
          onClick={() => loadEntries(search || undefined)}
        >
          Search
        </Button>
      </div>

      {/* Entries List */}
      {loading ? (
        <div className="flex justify-center py-12">
          <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
        </div>
      ) : error ? (
        <div className="rounded-xl border border-destructive/20 bg-destructive/5 p-6 text-center text-sm text-destructive">
          {error}
        </div>
      ) : entries.length === 0 ? (
        <div className="rounded-xl border border-dashed p-12 text-center">
          <BookOpen className="mx-auto mb-3 h-10 w-10 text-muted-foreground/50" />
          <p className="text-muted-foreground">No journal entries yet</p>
          <p className="text-xs text-muted-foreground/70 mt-1">
            Write your first entry above
          </p>
        </div>
      ) : (
        <div className="space-y-2">
          {entries.map((entry) => (
            <button
              key={entry.id}
              onClick={() => setViewEntry(entry)}
              className="w-full text-left rounded-xl border border-l-4 bg-card p-4 transition-colors hover:bg-accent group"
              style={{
                borderLeftColor: entry.mood_label
                  ? getMoodColor(entry.mood_label)
                  : undefined,
              }}
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1 min-w-0">
                  <p className="text-sm line-clamp-2 text-foreground">
                    {entry.content}
                  </p>
                  <div className="flex items-center gap-2 mt-2 flex-wrap">
                    <span className="text-xs text-muted-foreground flex items-center gap-1">
                      <Calendar className="h-3 w-3" />
                      {formatDate(entry.created_at)}
                    </span>
                    {entry.mood_label && (
                      <Badge
                        variant="secondary"
                        className="text-[10px] capitalize h-5"
                      >
                        {entry.mood_label}
                      </Badge>
                    )}
                    {entry.themes?.slice(0, 2).map((t, i) => (
                      <Badge
                        key={i}
                        variant="outline"
                        className="text-[10px] h-5"
                      >
                        {t}
                      </Badge>
                    ))}
                    {(entry.themes?.length ?? 0) > 2 && (
                      <span className="text-[10px] text-muted-foreground">
                        +{entry.themes.length - 2}
                      </span>
                    )}
                  </div>
                </div>
                <Pencil className="h-4 w-4 text-muted-foreground/0 group-hover:text-muted-foreground transition-colors shrink-0 mt-1" />
              </div>
            </button>
          ))}
        </div>
      )}

      {/* Detail Dialog */}
      <Dialog open={!!viewEntry} onOpenChange={() => setViewEntry(null)}>
        <DialogContent
          className="max-w-2xl max-h-[80vh] overflow-y-auto border-l-4"
          style={{
            borderLeftColor: viewEntry?.mood_label
              ? getMoodColor(viewEntry.mood_label)
              : undefined,
          }}
        >
          {viewEntry && (
            <>
              <DialogHeader>
                <DialogTitle className="flex items-center gap-3">
                  <span className="text-base">Journal Entry</span>
                  {viewEntry.mood_label && (
                    <Badge variant="secondary" className="capitalize">
                      {viewEntry.mood_label}
                    </Badge>
                  )}
                </DialogTitle>
                <p className="text-xs text-muted-foreground">
                  {formatDateFull(viewEntry.created_at)}
                </p>
              </DialogHeader>

              <div className="mt-4 space-y-4">
                <p className="text-sm whitespace-pre-wrap leading-relaxed">
                  {viewEntry.content}
                </p>

                {(viewEntry.themes?.length > 0 ||
                  viewEntry.entities?.length > 0) && (
                  <div className="rounded-lg bg-muted/50 p-3 space-y-2">
                    {viewEntry.themes?.length > 0 && (
                      <div className="flex items-center gap-2 flex-wrap">
                        <Tag className="h-3.5 w-3.5 text-muted-foreground" />
                        {viewEntry.themes.map((t, i) => (
                          <Badge
                            key={i}
                            variant="outline"
                            className="text-xs"
                          >
                            {t}
                          </Badge>
                        ))}
                      </div>
                    )}
                    {viewEntry.entities?.length > 0 && (
                      <div className="flex items-center gap-2 flex-wrap">
                        <User className="h-3.5 w-3.5 text-muted-foreground" />
                        {viewEntry.entities.map((e, i) => (
                          <Badge
                            key={i}
                            variant="secondary"
                            className="text-xs"
                          >
                            {e}
                          </Badge>
                        ))}
                      </div>
                    )}
                  </div>
                )}

                <div className="flex justify-between">
                  {confirmDelete === viewEntry.id ? (
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-destructive">Delete this entry?</span>
                      <Button
                        size="sm"
                        variant="destructive"
                        onClick={() => handleDelete(viewEntry.id)}
                        disabled={deleting}
                        className="gap-1"
                      >
                        {deleting ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Trash2 className="h-3.5 w-3.5" />}
                        Confirm
                      </Button>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => setConfirmDelete(null)}
                      >
                        Cancel
                      </Button>
                    </div>
                  ) : (
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => setConfirmDelete(viewEntry.id)}
                      className="gap-2 text-muted-foreground hover:text-destructive"
                    >
                      <Trash2 className="h-3.5 w-3.5" /> Delete
                    </Button>
                  )}
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => startEdit(viewEntry)}
                    className="gap-2"
                  >
                    <Pencil className="h-3.5 w-3.5" /> Edit Entry
                  </Button>
                </div>
              </div>
            </>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
