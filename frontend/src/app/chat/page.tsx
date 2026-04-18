"use client";

import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/auth";
import {
  streamMessage,
  getMessages,
  updateMessageApi,
  createChatSession,
  getChatSessions,
  deleteChatSession,
} from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import {
  Send,
  Pencil,
  Check,
  X,
  Bot,
  User,
  Plus,
  MessageSquare,
  Trash2,
  PanelLeftClose,
  PanelLeft,
} from "lucide-react";
import { Markdown } from "@/components/markdown";

interface Message {
  id?: number;
  role: string;
  content: string;
  intent?: string;
  tool_class?: string;
  created_at?: string;
}

interface ChatSession {
  id: number;
  title: string;
  created_at: string;
  updated_at: string | null;
}

export default function ChatPage() {
  const { email } = useAuth();
  const router = useRouter();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [streaming, setStreaming] = useState("");
  const [editingIdx, setEditingIdx] = useState<number | null>(null);
  const [editContent, setEditContent] = useState("");
  const scrollRef = useRef<HTMLDivElement>(null);

  // Sessions
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [currentSessionId, setCurrentSessionId] = useState<number | null>(null);
  const [showSessions, setShowSessions] = useState(true);
  const [deletingSession, setDeletingSession] = useState<number | null>(null);

  useEffect(() => {
    if (!email) {
      router.push("/");
      return;
    }
    loadSessions();
  }, [email, router]);

  const loadSessions = async () => {
    if (!email) return;
    try {
      const data = await getChatSessions(email);
      setSessions(data.sessions);
      // Load most recent session, or create one if none exist
      if (data.sessions.length > 0) {
        const latestId = data.sessions[0].id;
        setCurrentSessionId(latestId);
        loadMessages(latestId);
      } else {
        handleNewChat();
      }
    } catch {}
  };

  const loadMessages = async (sessionId: number) => {
    if (!email) return;
    try {
      const data = await getMessages(email, 50, sessionId);
      setMessages(data.messages);
    } catch {}
  };

  const handleNewChat = async () => {
    if (!email) return;
    try {
      const session = await createChatSession(email);
      setCurrentSessionId(session.id);
      setMessages([]);
      setSessions((prev) => [
        { ...session, updated_at: null },
        ...prev,
      ]);
    } catch {}
  };

  const handleSelectSession = (sessionId: number) => {
    setCurrentSessionId(sessionId);
    setMessages([]);
    setStreaming("");
    setLoading(false);
    loadMessages(sessionId);
  };

  const handleDeleteSession = async (sessionId: number) => {
    if (!email) return;
    try {
      await deleteChatSession(email, sessionId);
      setSessions((prev) => prev.filter((s) => s.id !== sessionId));
      setDeletingSession(null);
      // If we deleted the current session, switch to another or create new
      if (currentSessionId === sessionId) {
        const remaining = sessions.filter((s) => s.id !== sessionId);
        if (remaining.length > 0) {
          handleSelectSession(remaining[0].id);
        } else {
          handleNewChat();
        }
      }
    } catch {}
  };

  useEffect(() => {
    if (!editingIdx) {
      scrollRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, streaming, editingIdx]);

  const handleSend = async () => {
    if (!input.trim() || !email || loading) return;

    const userMsg = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: userMsg }]);
    setLoading(true);
    setStreaming("");

    let fullResponse = "";
    let meta = { intent: "", tool_class: "" };

    try {
      await streamMessage(
        email,
        userMsg,
        (token) => {
          fullResponse += token;
          setStreaming(fullResponse);
        },
        (m) => {
          meta = m;
        },
        () => {
          setMessages((prev) => [
            ...prev,
            {
              role: "assistant",
              content: fullResponse,
              intent: meta.intent,
              tool_class: meta.tool_class,
            },
          ]);
          setStreaming("");
          setLoading(false);

          // Re-fetch messages to get proper IDs + refresh sessions for title
          if (email && currentSessionId) {
            getMessages(email, 50, currentSessionId)
              .then((data) => setMessages(data.messages))
              .catch(() => {});
            getChatSessions(email)
              .then((data) => setSessions(data.sessions))
              .catch(() => {});
          }
        },
        currentSessionId
      );
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Something went wrong. Please try again.",
        },
      ]);
      setStreaming("");
      setLoading(false);
    }
  };

  const handleEditSave = async (idx: number) => {
    const msg = messages[idx];
    if (!email || !msg.id || !editContent.trim()) return;

    try {
      await updateMessageApi(email, msg.id, editContent);
      setMessages((prev) =>
        prev.map((m, i) => (i === idx ? { ...m, content: editContent } : m))
      );
    } catch {
      // ignore
    }
    setEditingIdx(null);
    setEditContent("");
  };

  if (!email) return null;

  const formatSessionDate = (d: string) => {
    const date = new Date(d);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    if (days === 0) return "Today";
    if (days === 1) return "Yesterday";
    if (days < 7) return `${days}d ago`;
    return date.toLocaleDateString("en-US", { month: "short", day: "numeric" });
  };

  return (
    <div className="flex h-screen pt-14 md:pt-0">
      {/* Session sidebar */}
      {showSessions && (
        <div className="hidden md:flex w-64 flex-col border-r bg-muted/20">
          <div className="p-3 border-b flex items-center justify-between">
            <Button
              size="sm"
              onClick={handleNewChat}
              className="flex-1 gap-2"
            >
              <Plus className="h-4 w-4" /> New Chat
            </Button>
            <Button
              size="icon"
              variant="ghost"
              className="h-8 w-8 ml-1 shrink-0"
              onClick={() => setShowSessions(false)}
            >
              <PanelLeftClose className="h-4 w-4" />
            </Button>
          </div>
          <ScrollArea className="flex-1">
            <div className="p-2 space-y-1">
              {sessions.map((session) => (
                <div
                  key={session.id}
                  className={`group flex items-center gap-2 rounded-lg px-3 py-2 text-sm cursor-pointer transition-colors ${
                    currentSessionId === session.id
                      ? "bg-accent text-accent-foreground"
                      : "hover:bg-accent/50 text-muted-foreground"
                  }`}
                  onClick={() => handleSelectSession(session.id)}
                >
                  <MessageSquare className="h-3.5 w-3.5 shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="truncate text-xs font-medium">
                      {session.title}
                    </p>
                    <p className="text-[10px] text-muted-foreground/70">
                      {formatSessionDate(session.created_at)}
                    </p>
                  </div>
                  {deletingSession === session.id ? (
                    <div className="flex gap-0.5">
                      <Button
                        size="icon"
                        variant="ghost"
                        className="h-6 w-6 text-destructive"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDeleteSession(session.id);
                        }}
                      >
                        <Check className="h-3 w-3" />
                      </Button>
                      <Button
                        size="icon"
                        variant="ghost"
                        className="h-6 w-6"
                        onClick={(e) => {
                          e.stopPropagation();
                          setDeletingSession(null);
                        }}
                      >
                        <X className="h-3 w-3" />
                      </Button>
                    </div>
                  ) : (
                    <Button
                      size="icon"
                      variant="ghost"
                      className="h-6 w-6 opacity-0 group-hover:opacity-100 text-muted-foreground hover:text-destructive"
                      onClick={(e) => {
                        e.stopPropagation();
                        setDeletingSession(session.id);
                      }}
                    >
                      <Trash2 className="h-3 w-3" />
                    </Button>
                  )}
                </div>
              ))}
            </div>
          </ScrollArea>
        </div>
      )}

      {/* Main chat area */}
      <div className="flex flex-1 flex-col min-w-0">
        <header className="border-b p-4 page-header-gradient flex items-center gap-3">
          {!showSessions && (
            <Button
              size="icon"
              variant="ghost"
              className="h-8 w-8 hidden md:flex"
              onClick={() => setShowSessions(true)}
            >
              <PanelLeft className="h-4 w-4" />
            </Button>
          )}
          <div className="flex-1">
            <h1 className="text-lg font-semibold">Chat with MindMate</h1>
            <p className="text-sm text-muted-foreground">
              Journaling, mood tracking, self-care advice, and therapy support
            </p>
          </div>
          <Button
            size="sm"
            variant="outline"
            onClick={handleNewChat}
            className="gap-1.5 md:hidden"
          >
            <Plus className="h-3.5 w-3.5" /> New
          </Button>
        </header>

        <ScrollArea className="flex-1 p-4">
          <div className="mx-auto max-w-2xl space-y-4">
            {messages.length === 0 && !streaming && (
              <div className="flex h-64 flex-col items-center justify-center text-center">
                <div className="flex h-16 w-16 items-center justify-center rounded-full bg-primary/10 mb-4">
                  <Bot className="h-8 w-8 text-primary/60" />
                </div>
                <p className="text-muted-foreground font-medium">
                  Start a conversation
                </p>
                <p className="text-sm text-muted-foreground/70 mt-1">
                  How are you feeling today?
                </p>
              </div>
            )}

            {messages.map((msg, i) => (
              <div
                key={msg.id ?? i}
                className={`group flex items-end gap-2 ${msg.role === "user" ? "justify-end" : "justify-start"}`}
              >
                {msg.role === "assistant" && (
                  <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-primary/10 mb-1">
                    <Bot className="h-3.5 w-3.5 text-primary" />
                  </div>
                )}

                <div
                  className={`relative max-w-[80%] rounded-2xl px-4 py-3 text-sm ${
                    msg.role === "user"
                      ? "bg-primary text-primary-foreground shadow-sm"
                      : "bg-accent/50 shadow-[0_1px_3px_0_oklch(0_0_0/0.04)]"
                  }`}
                >
                  {editingIdx === i ? (
                    <div className="space-y-2">
                      <Textarea
                        value={editContent}
                        onChange={(e) => setEditContent(e.target.value)}
                        className="min-h-[60px] bg-background text-foreground"
                        rows={2}
                      />
                      <div className="flex gap-1 justify-end">
                        <Button
                          size="icon"
                          variant="ghost"
                          className="h-7 w-7"
                          onClick={() => handleEditSave(i)}
                        >
                          <Check className="h-3 w-3" />
                        </Button>
                        <Button
                          size="icon"
                          variant="ghost"
                          className="h-7 w-7"
                          onClick={() => setEditingIdx(null)}
                        >
                          <X className="h-3 w-3" />
                        </Button>
                      </div>
                    </div>
                  ) : (
                    <>
                      {msg.role === "assistant" ? (
                        <Markdown content={msg.content} />
                      ) : (
                        <div className="whitespace-pre-wrap">{msg.content}</div>
                      )}
                      {msg.role === "user" && msg.id && (
                        <button
                          className="absolute -left-8 top-2 hidden group-hover:block text-muted-foreground hover:text-foreground"
                          onClick={() => {
                            setEditingIdx(i);
                            setEditContent(msg.content);
                          }}
                        >
                          <Pencil className="h-3.5 w-3.5" />
                        </button>
                      )}
                      {msg.intent && msg.role === "assistant" && (
                        <div className="mt-2 flex gap-1">
                          <Badge variant="secondary" className="text-xs">
                            {msg.intent}
                          </Badge>
                          {msg.tool_class && (
                            <Badge variant="outline" className="text-xs">
                              {msg.tool_class}
                            </Badge>
                          )}
                        </div>
                      )}
                    </>
                  )}
                  {msg.created_at && (
                    <div className="mt-1 text-[10px] opacity-0 group-hover:opacity-60 transition-opacity text-muted-foreground">
                      {new Date(msg.created_at).toLocaleString()}
                    </div>
                  )}
                </div>

                {msg.role === "user" && (
                  <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-primary mb-1">
                    <User className="h-3.5 w-3.5 text-primary-foreground" />
                  </div>
                )}
              </div>
            ))}

            {streaming && (
              <div className="flex items-end gap-2 justify-start">
                <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-primary/10 mb-1">
                  <Bot className="h-3.5 w-3.5 text-primary" />
                </div>
                <div className="max-w-[80%] rounded-2xl bg-accent/50 px-4 py-3 text-sm shadow-[0_1px_3px_0_oklch(0_0_0/0.04)]">
                  <Markdown content={streaming} />
                </div>
              </div>
            )}

            {loading && !streaming && (
              <div className="flex items-end gap-2 justify-start">
                <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-primary/10 mb-1">
                  <Bot className="h-3.5 w-3.5 text-primary" />
                </div>
                <div className="rounded-2xl bg-accent/50 px-4 py-3 shadow-[0_1px_3px_0_oklch(0_0_0/0.04)]">
                  <div className="flex items-center gap-1">
                    <span className="typing-dot h-2 w-2 rounded-full bg-muted-foreground/60" />
                    <span className="typing-dot h-2 w-2 rounded-full bg-muted-foreground/60" />
                    <span className="typing-dot h-2 w-2 rounded-full bg-muted-foreground/60" />
                  </div>
                </div>
              </div>
            )}

            <div ref={scrollRef} />
          </div>
        </ScrollArea>

        <div className="border-t p-4">
          <div className="mx-auto flex max-w-2xl gap-2">
            <Textarea
              placeholder="How are you feeling today?"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  handleSend();
                }
              }}
              className="min-h-[44px] max-h-32 resize-none"
              rows={1}
            />
            <Button
              onClick={handleSend}
              disabled={!input.trim() || loading}
              size="icon"
            >
              <Send className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
