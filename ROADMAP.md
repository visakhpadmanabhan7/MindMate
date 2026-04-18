# MindMate: Next Iterations Roadmap

## Current State (committed: 64240b0)

Full-stack rebuild complete. All features working end-to-end:
- Chat with streaming SSE, conversation memory, passive mood detection
- Journal with auto mood/theme/entity extraction, dedicated editor
- Therapy companion: session parsing, cross-session patterns, therapy-aware recall
- Mood dashboard with clickable data points and source tracking
- Knowledge base: upload/delete/search PDFs
- Crisis guardrails (988 hotline)
- 100% free stack: Groq (Llama 3.3 70B) + sentence-transformers + SQLite + ChromaDB
- 22 passing tests, ruff clean

---

## Iteration 1: UI/UX Redesign (Visual Identity)

**Goal:** Make it look like a real product — calm, warm, professional for mental health.

### 1A. Design System & Theme
- Proper color palette in `globals.css` — warm neutrals, calming accent (sage green or soft blue)
- Mood-specific colors: happy=green, sad=blue, anxious=amber, angry=red, calm=teal
- Subtle gradients on page headers
- Consistent spacing, card radius, shadow depth

### 1B. Chat Page Polish
- Markdown rendering in assistant messages (`react-markdown` + `remark-gfm`)
- Better message bubbles — shadows, avatars, rounded corners
- Typing indicator (3 bouncing dots) instead of "Thinking..."
- Timestamps on hover

### 1C. Dashboard Redesign
- Colored stat cards with accent gradients
- Custom chart tooltips, gradient line fill, animations
- Mood-colored dots on chart (green=happy, red=angry)
- Better empty states

### 1D. Journal Page Polish
- Left-colored border on entry cards based on mood
- Better theme cloud with weighted font sizes
- Smooth expand/collapse

### 1E. Therapy Page Polish
- Numbered session badges, timeline connecting sessions
- Color-coded action items

### 1F. Knowledge Base Polish
- Better document cards, highlighted search matches

**Add deps:** `react-markdown`, `remark-gfm`
**New file:** `frontend/src/components/markdown.tsx`

---

## Iteration 2: Bug Fixes

- **Journal edit** — `update_journal_entry` returns "Entry not found" for chat-created entries. Debug user_id matching.
- **Chat message edit** — verify IDs flow correctly from API to frontend
- **Mood source icons** — null checks when source counts are 0
- **Mobile layout** — test all pages, fix overflow/spacing

---

## Iteration 3: Content Quality

- Better RAG responses — follow-up suggestions, "no relevant info" fallback
- Semantic matching for therapy recall (embeddings instead of keyword overlap)
- Improved journal analysis prompt (better themes, sentiment score)
- Markdown styling in chat responses

---

## Iteration 4: Advanced Features

- **Weekly summary** — LLM-generated recap (mood trends + journal themes + therapy progress)
- **Goal tracking** — set wellness goals, track progress from actual data
- **Chat history search** — search past messages, filter by intent
- **JWT auth** — replace localStorage email with proper tokens (deployment-ready)

---

## Iteration 5: Deployment

- Docker Compose production config (PostgreSQL + pgvector + Nginx)
- Vercel frontend deployment
- GitHub Actions CI/CD (tests + lint + build on PR)

---

## Priority Order

1. **Iteration 1** — UI/UX (most visible impact)
2. **Iteration 2** — Bug fixes
3. **Iteration 3** — Content quality
4. Iteration 4 — Advanced features (stretch)
5. Iteration 5 — Deployment (when ready)
