const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: "Request failed" }));
    // Auto-logout on 404 "User not found" (stale session)
    if (res.status === 404 && error.detail?.includes("User not found")) {
      localStorage.removeItem("mindmate_email");
      window.location.href = "/";
      throw new Error("Session expired. Please log in again.");
    }
    throw new Error(error.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

// --- Auth ---

export async function registerUser(email: string, password: string, name?: string) {
  return apiFetch<{ status: string; user: { id: string; email: string; name: string } }>(
    "/api/v1/register_user",
    { method: "POST", body: JSON.stringify({ email, password, name }) }
  );
}

export async function loginUser(email: string, password: string) {
  return apiFetch<{ status: string; email: string; name: string }>(
    "/api/v1/login",
    { method: "POST", body: JSON.stringify({ email, password }) }
  );
}

// --- Chat Sessions ---

export async function createChatSession(email: string) {
  return apiFetch<{ id: number; title: string; created_at: string }>(
    "/api/v1/chat/sessions",
    { method: "POST", body: JSON.stringify({ email }) }
  );
}

export async function getChatSessions(email: string, limit = 50) {
  return apiFetch<{
    sessions: { id: number; title: string; created_at: string; updated_at: string | null }[];
  }>(`/api/v1/chat/sessions?email=${encodeURIComponent(email)}&limit=${limit}`);
}

export async function deleteChatSession(email: string, sessionId: number) {
  return apiFetch<{ status: string; id: number }>(
    `/api/v1/chat/sessions/${sessionId}?email=${encodeURIComponent(email)}`,
    { method: "DELETE" }
  );
}

// --- Chat ---

export async function sendMessage(email: string, message: string) {
  return apiFetch<{ response: string; intent: string; tool_class: string; email: string }>(
    "/api/v1/chat",
    { method: "POST", body: JSON.stringify({ email, message }) }
  );
}

export async function streamMessage(
  email: string,
  message: string,
  onToken: (token: string) => void,
  onMeta: (meta: { intent: string; tool_class: string }) => void,
  onDone: () => void,
  sessionId?: number | null
) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 120000);

  try {
    const res = await fetch(`${API_URL}/api/v1/chat/stream`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, message, session_id: sessionId ?? null }),
      signal: controller.signal,
    });

    if (!res.ok) throw new Error("Stream request failed");
    const reader = res.body?.getReader();
    if (!reader) throw new Error("No reader");

    const decoder = new TextDecoder();
    let buffer = "";

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";
        for (const line of lines) {
          if (line.startsWith("data: ")) {
            try {
              const data = JSON.parse(line.slice(6));
              if (data.type === "meta") onMeta(data);
              else if (data.type === "token") onToken(data.content);
              else if (data.type === "done") onDone();
            } catch { /* skip malformed */ }
          }
        }
      }
    } finally {
      reader.cancel();
    }
  } finally {
    clearTimeout(timeout);
  }
}

// --- Messages ---

export async function getMessages(email: string, limit = 50, sessionId?: number | null) {
  let url = `/api/v1/messages?email=${encodeURIComponent(email)}&limit=${limit}`;
  if (sessionId) url += `&session_id=${sessionId}`;
  return apiFetch<{ messages: { id: number; role: string; content: string; intent?: string; tool_class?: string; created_at?: string }[] }>(
    url
  );
}

export async function searchMessages(email: string, query?: string, intent?: string, limit = 50) {
  let url = `/api/v1/messages/search?email=${encodeURIComponent(email)}&limit=${limit}`;
  if (query) url += `&q=${encodeURIComponent(query)}`;
  if (intent) url += `&intent=${encodeURIComponent(intent)}`;
  return apiFetch<{ messages: { id: number; role: string; content: string; intent?: string; tool_class?: string; created_at?: string }[] }>(
    url
  );
}

export async function updateMessageApi(email: string, messageId: number, content: string) {
  return apiFetch<{ id: number; content: string; updated_at: string }>(
    `/api/v1/messages/${messageId}`,
    { method: "PUT", body: JSON.stringify({ email, content }) }
  );
}

// --- Journal ---

export async function getJournalEntries(email: string, limit = 20, offset = 0, search?: string) {
  let url = `/api/v1/journal/entries?email=${encodeURIComponent(email)}&limit=${limit}&offset=${offset}`;
  if (search) url += `&search=${encodeURIComponent(search)}`;
  return apiFetch<{
    entries: {
      id: number;
      content: string;
      mood_label: string | null;
      themes: string[];
      entities: string[];
      sentiment_score: number | null;
      summary: string | null;
      created_at: string;
      updated_at: string | null;
    }[];
    count: number;
  }>(url);
}

export async function createJournalEntry(email: string, content: string) {
  return apiFetch<{
    id: number;
    content: string;
    mood_label: string;
    themes: string[];
    entities: string[];
    created_at: string;
  }>("/api/v1/journal/entries", {
    method: "POST",
    body: JSON.stringify({ email, content }),
  });
}

export async function updateJournalEntry(email: string, entryId: number, content: string) {
  return apiFetch<{
    id: number;
    content: string;
    mood_label: string;
    themes: string[];
    entities: string[];
    updated_at: string;
  }>(`/api/v1/journal/entries/${entryId}`, {
    method: "PUT",
    body: JSON.stringify({ email, content }),
  });
}

export async function deleteJournalEntry(email: string, entryId: number) {
  return apiFetch<{ status: string; id: number }>(
    `/api/v1/journal/entries/${entryId}?email=${encodeURIComponent(email)}`,
    { method: "DELETE" }
  );
}

export async function getJournalThemes(email: string) {
  return apiFetch<{ themes: { name: string; count: number }[] }>(
    `/api/v1/journal/themes?email=${encodeURIComponent(email)}`
  );
}

// --- Mood ---

export async function getMoodAnalytics(email: string) {
  return apiFetch<{
    timeline: {
      id: number;
      date: string;
      mood: string;
      message: string;
      source_type: string;
      source_id: number | null;
      timestamp: string;
    }[];
    distribution: Record<string, number>;
    total_entries: number;
    streak: number;
    sources: Record<string, number>;
  }>(`/api/v1/mood/analytics?email=${encodeURIComponent(email)}`);
}

export async function getMoodDetail(email: string, moodId: number) {
  return apiFetch<{
    id: number;
    mood: string;
    message: string;
    timestamp: string;
    source_type: string;
    source_id: number | null;
    source_content: string | null;
  }>(`/api/v1/mood/${moodId}/detail?email=${encodeURIComponent(email)}`);
}

// --- Therapy ---

export async function createTherapySession(
  email: string,
  data: {
    issues_discussed: string[];
    learnings: string;
    action_items: string[];
    techniques: string[];
    date?: string;
  }
) {
  return apiFetch<{ session_number: number; status: string }>(
    "/api/v1/therapy/sessions",
    { method: "POST", body: JSON.stringify({ email, ...data }) }
  );
}

export async function getTherapySessions(email: string, limit = 10) {
  return apiFetch<{
    sessions: {
      id: number;
      session_number: number;
      date: string;
      issues_discussed: string[];
      learnings: string;
      action_items: string[];
      techniques: string[];
      created_at: string;
    }[];
  }>(`/api/v1/therapy/sessions?email=${encodeURIComponent(email)}&limit=${limit}`);
}

export async function updateTherapySession(
  email: string,
  sessionId: number,
  updates: {
    issues_discussed?: string[];
    learnings?: string;
    action_items?: string[];
    techniques?: string[];
    raw_notes?: string;
  }
) {
  return apiFetch(`/api/v1/therapy/sessions/${sessionId}`, {
    method: "PUT",
    body: JSON.stringify({ email, ...updates }),
  });
}

// --- Knowledge Base ---

export async function listDocuments() {
  return apiFetch<{
    documents: { name: string; size_kb: number; chunks: number; indexed: boolean }[];
  }>("/api/v1/knowledge/documents");
}

export async function uploadDocument(file: File) {
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch(`${API_URL}/api/v1/knowledge/upload`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: "Upload failed" }));
    throw new Error(error.detail);
  }
  return res.json() as Promise<{ status: string; filename: string; chunks: number; pages: number }>;
}

export async function deleteDocument(filename: string) {
  return apiFetch<{ status: string; filename: string; vectors_removed: number }>(
    `/api/v1/knowledge/${encodeURIComponent(filename)}`,
    { method: "DELETE" }
  );
}

export async function searchKnowledgeBase(query: string, k = 5) {
  return apiFetch<{
    results: { content: string; source_doc: string; page_number: number | null; relevance: number }[];
    query: string;
  }>("/api/v1/knowledge/search", {
    method: "POST",
    body: JSON.stringify({ query, k }),
  });
}

// --- Weekly Summary ---

export async function getWeeklySummary(email: string) {
  return apiFetch<{
    period: string;
    summary: string;
    stats: { mood_entries: number; journal_entries: number; therapy_sessions: number };
    generated_at: string;
  }>(`/api/v1/summary/weekly?email=${encodeURIComponent(email)}`);
}

// --- Export ---

export function getExportUrl(email: string) {
  return `${API_URL}/api/v1/export?email=${encodeURIComponent(email)}`;
}
