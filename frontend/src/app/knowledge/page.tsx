"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/auth";
import {
  listDocuments,
  uploadDocument,
  deleteDocument,
  searchKnowledgeBase,
} from "@/lib/api";
import { useToast } from "@/components/ui/toast";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import {
  FileText,
  Upload,
  Trash2,
  Search,
  Loader2,
  BookOpen,
  Database,
  Layers,
  AlertTriangle,
  Check,
} from "lucide-react";

interface DocInfo {
  name: string;
  size_kb: number;
  chunks: number;
  indexed: boolean;
}

interface SearchResult {
  content: string;
  source_doc: string;
  page_number: number | null;
  relevance: number;
}

export default function KnowledgePage() {
  const { email } = useAuth();
  const router = useRouter();
  const { toast } = useToast();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [docs, setDocs] = useState<DocInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadStep, setUploadStep] = useState("");
  const [uploadDone, setUploadDone] = useState<string | null>(null);
  const [dragOver, setDragOver] = useState(false);

  // Search
  const [searchQuery, setSearchQuery] = useState("");
  const [searching, setSearching] = useState(false);
  const [searchResults, setSearchResults] = useState<SearchResult[] | null>(null);

  // Delete confirmation
  const [deleteTarget, setDeleteTarget] = useState<string | null>(null);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    if (!email) { router.push("/"); return; }
    loadDocs();
  }, [email, router]);

  const loadDocs = async () => {
    setLoading(true);
    try {
      const data = await listDocuments();
      setDocs(data.documents);
    } catch {}
    setLoading(false);
  };

  const handleUpload = async (file: File) => {
    if (!file.name.toLowerCase().endsWith(".pdf")) return;
    setUploading(true);
    setUploadDone(null);
    setUploadProgress(0);
    setUploadStep("Uploading file...");

    // Simulate progress steps while the actual upload+indexing runs
    const progressTimer = setInterval(() => {
      setUploadProgress((prev) => {
        if (prev < 20) { setUploadStep("Uploading file..."); return prev + 4; }
        if (prev < 50) { setUploadStep("Extracting text from PDF..."); return prev + 2; }
        if (prev < 75) { setUploadStep("Splitting into chunks..."); return prev + 1; }
        if (prev < 90) { setUploadStep("Generating embeddings..."); return prev + 0.5; }
        return prev;
      });
    }, 200);

    try {
      const result = await uploadDocument(file);
      clearInterval(progressTimer);
      setUploadProgress(100);
      setUploadStep("Done!");
      setUploadDone(`${file.name} — ${result.chunks} chunks indexed from ${result.pages} pages`);
      toast("Document indexed successfully", "success");
      await loadDocs();
    } catch {
      clearInterval(progressTimer);
      setUploadDone("Upload failed. Please try again.");
      toast("Upload failed", "error");
    }

    setTimeout(() => {
      setUploading(false);
      setUploadProgress(0);
    }, 1000);
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleUpload(file);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) handleUpload(file);
  }, []);

  const handleDelete = async () => {
    if (!deleteTarget) return;
    setDeleting(true);
    try {
      await deleteDocument(deleteTarget);
      await loadDocs();
      setSearchResults(null);
      toast("Document deleted", "success");
    } catch {
      toast("Delete failed", "error");
    }
    setDeleting(false);
    setDeleteTarget(null);
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    setSearching(true);
    try {
      const data = await searchKnowledgeBase(searchQuery, 6);
      setSearchResults(data.results);
    } catch {}
    setSearching(false);
  };

  const formatSize = (kb: number) =>
    kb > 1024 ? `${(kb / 1024).toFixed(1)} MB` : `${kb} KB`;

  const cleanTitle = (name: string) =>
    name.replace(/\.pdf$/i, "").replace(/[-_]+/g, " ").replace(/\s*\(z-lib\.org\)/i, "").trim();

  const highlightQuery = (text: string, query: string) => {
    if (!query.trim()) return text;
    const escaped = query.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    const parts = text.split(new RegExp(`(${escaped})`, "gi"));
    return parts.map((part, i) =>
      part.toLowerCase() === query.toLowerCase() ? (
        <mark key={i} className="bg-primary/20 text-foreground rounded-sm px-0.5">{part}</mark>
      ) : part
    );
  };

  if (!email) return null;

  const totalChunks = docs.reduce((a, d) => a + d.chunks, 0);

  return (
    <div className="p-6 pt-20 md:pt-6 max-w-4xl mx-auto space-y-8">
      <div className="rounded-xl p-6 page-header-gradient">
        <h1 className="text-2xl font-bold">Knowledge Base</h1>
        <p className="text-sm text-muted-foreground mt-1">
          Manage the documents that power MindMate&apos;s evidence-based advice
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        <div className="rounded-xl border bg-card p-4 text-center">
          <FileText className="h-5 w-5 mx-auto text-muted-foreground mb-1" />
          <p className="text-2xl font-bold">{docs.length}</p>
          <p className="text-xs text-muted-foreground">Documents</p>
        </div>
        <div className="rounded-xl border bg-card p-4 text-center">
          <Layers className="h-5 w-5 mx-auto text-muted-foreground mb-1" />
          <p className="text-2xl font-bold">{totalChunks.toLocaleString()}</p>
          <p className="text-xs text-muted-foreground">Indexed Chunks</p>
        </div>
        <div className="rounded-xl border bg-card p-4 text-center">
          <Database className="h-5 w-5 mx-auto text-muted-foreground mb-1" />
          <p className="text-2xl font-bold">{formatSize(docs.reduce((a, d) => a + d.size_kb, 0))}</p>
          <p className="text-xs text-muted-foreground">Total Size</p>
        </div>
      </div>

      {/* Upload zone */}
      <div
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
        className={`rounded-xl border-2 border-dashed p-6 transition-colors ${
          dragOver ? "border-primary bg-primary/5" : "border-muted-foreground/20"
        }`}
      >
        {uploading ? (
          <div className="space-y-3">
            <div className="flex items-center justify-between text-sm">
              <span className="font-medium">{uploadStep}</span>
              <span className="text-muted-foreground">{Math.round(uploadProgress)}%</span>
            </div>
            <div className="h-2 rounded-full bg-muted overflow-hidden">
              <div
                className="h-full rounded-full bg-primary transition-all duration-300 ease-out"
                style={{ width: `${uploadProgress}%` }}
              />
            </div>
          </div>
        ) : (
          <div className="flex items-center gap-4">
            <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-muted">
              <Upload className="h-5 w-5 text-muted-foreground" />
            </div>
            <div className="flex-1">
              <p className="text-sm font-medium">Upload a document</p>
              <p className="text-xs text-muted-foreground">
                Drop a PDF here or click to browse. It will be indexed for evidence-based retrieval.
              </p>
            </div>
            <input ref={fileInputRef} type="file" accept=".pdf" onChange={handleFileInput} className="hidden" />
            <Button size="sm" variant="outline" onClick={() => fileInputRef.current?.click()} className="gap-2 shrink-0">
              <Upload className="h-4 w-4" /> Browse
            </Button>
          </div>
        )}

        {uploadDone && !uploading && (
          <div className="mt-3 flex items-center gap-2 rounded-lg bg-green-500/10 px-3 py-2 text-xs text-green-700">
            <Check className="h-3.5 w-3.5 shrink-0" />
            <span>{uploadDone}</span>
          </div>
        )}
      </div>

      {/* Search the knowledge base */}
      <div>
        <h2 className="text-sm font-medium text-muted-foreground mb-3 uppercase tracking-wider">
          Search Knowledge Base
        </h2>
        <div className="flex gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="e.g., breathing techniques for anxiety..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSearch()}
              className="pl-9"
            />
          </div>
          <Button onClick={handleSearch} disabled={!searchQuery.trim() || searching}>
            {searching ? <Loader2 className="h-4 w-4 animate-spin" /> : "Search"}
          </Button>
        </div>

        {searchResults && (
          <div className="mt-4 space-y-2">
            {searchResults.length === 0 ? (
              <p className="text-sm text-muted-foreground text-center py-4">No relevant results found</p>
            ) : (
              searchResults.map((r, i) => (
                <div key={i} className="rounded-lg border bg-card p-4 space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <FileText className="h-3.5 w-3.5 text-muted-foreground" />
                      <span className="text-xs font-medium">{cleanTitle(r.source_doc)}</span>
                      {r.page_number && (
                        <Badge variant="secondary" className="text-[10px] h-5">p. {r.page_number}</Badge>
                      )}
                    </div>
                    <Badge variant="outline" className="text-[10px] h-5">
                      {(r.relevance * 100).toFixed(0)}% match
                    </Badge>
                  </div>
                  <p className="text-sm text-muted-foreground leading-relaxed">{highlightQuery(r.content, searchQuery)}</p>
                </div>
              ))
            )}
          </div>
        )}
      </div>

      {/* Document List */}
      <div>
        <h2 className="text-sm font-medium text-muted-foreground mb-3 uppercase tracking-wider">
          Documents ({docs.length})
        </h2>
        {loading ? (
          <div className="flex justify-center py-8"><Loader2 className="h-6 w-6 animate-spin text-muted-foreground" /></div>
        ) : docs.length === 0 ? (
          <div className="rounded-xl border border-dashed p-8 text-center">
            <BookOpen className="mx-auto mb-2 h-8 w-8 text-muted-foreground/50" />
            <p className="text-sm text-muted-foreground">No documents yet. Upload your first PDF above.</p>
          </div>
        ) : (
          <div className="space-y-2">
            {docs.map((doc) => (
              <div key={doc.name} className="group flex items-center gap-4 rounded-xl border bg-card p-4 transition-colors hover:bg-accent/50">
                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-gradient-to-br from-primary/15 to-primary/5">
                  <FileText className="h-5 w-5 text-primary" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate">{cleanTitle(doc.name)}</p>
                  <div className="flex items-center gap-3 mt-1">
                    <span className="text-xs text-muted-foreground">{formatSize(doc.size_kb)}</span>
                    <span className="text-xs text-muted-foreground">{doc.chunks} chunks</span>
                    {doc.indexed && (
                      <Badge variant="secondary" className="text-[10px] h-4 bg-green-500/10 text-green-700">Indexed</Badge>
                    )}
                  </div>
                </div>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-8 w-8 opacity-0 group-hover:opacity-100 text-muted-foreground hover:text-destructive transition-opacity"
                  onClick={() => setDeleteTarget(doc.name)}
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Delete Confirmation Dialog */}
      <Dialog open={!!deleteTarget} onOpenChange={() => setDeleteTarget(null)}>
        <DialogContent className="max-w-sm">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-destructive" />
              Delete Document
            </DialogTitle>
            <DialogDescription>
              This will remove <strong>{deleteTarget && cleanTitle(deleteTarget)}</strong> and all its indexed data from the knowledge base. This cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <div className="flex justify-end gap-2 mt-4">
            <Button variant="outline" onClick={() => setDeleteTarget(null)}>Cancel</Button>
            <Button variant="destructive" onClick={handleDelete} disabled={deleting}>
              {deleting ? <Loader2 className="h-4 w-4 animate-spin mr-1" /> : <Trash2 className="h-4 w-4 mr-1" />}
              Delete
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
