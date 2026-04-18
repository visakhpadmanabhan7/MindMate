# MindMate: Roadmap

## Completed

### Iteration 1: UI/UX Redesign
- [x] Warm sage green + neutral theme with mood-specific colors (OKLCh)
- [x] Markdown rendering in chat (`react-markdown` + `remark-gfm`)
- [x] Chat avatars (Bot/User), bouncing typing indicator, timestamps on hover
- [x] Dashboard: mood-colored chart dots + pie slices, gradient stat cards, custom tooltips, gradient fill
- [x] Journal: mood-colored left borders, weighted theme cloud, header gradient
- [x] Therapy: timeline layout with numbered session badges, colored action items
- [x] Knowledge: search result highlighting, gradient document icons
- [x] Sidebar: gradient heart icon, sage green active state
- [x] Page header gradients across all pages

### Iteration 2: Bug Fixes + New Features
- [x] Fixed mood source null checks (pre-initialized sources dict)
- [x] Fixed journal edit for chat-created entries (returns entry_id, debug logging)
- [x] Fixed chat message IDs (re-fetch after streaming for edit button)
- [x] Mobile layout fixes (responsive grids, consistent padding)
- [x] **Chat sessions** — create/switch/delete conversations, session sidebar, auto-titles via LLM
- [x] **Journal deletion** — backend DELETE endpoint + frontend confirmation UI
- [x] **Therapy page creation** — "Log Session" form directly on therapy page
- [x] **Chat journal analysis** — entries created via chat now run full mood/theme extraction
- [x] Dashboard source labels ("Chat 50%", "Journal 50%", "Explicit 50%")
- [x] Toast notification system across all pages
- [x] Smart session titles (LLM-generated 3-5 word summaries)

### Iteration 3: Content Quality
- [x] **Split responses** — "Based on your history" (synthesizes moods + journals + therapy) + "What science says" (RAG with citations)
- [x] Enrichment only triggers on negative moods (no unsolicited advice for positive emotions)
- [x] Better RAG: relevance threshold (L2 > 1.5 fallback), "no info" response, follow-up suggestions
- [x] Improved journal analysis: sentiment_score (-1.0 to 1.0) + summary fields
- [x] Sentiment indicator on journal entry cards (green/amber/red dot)
- [x] Journal summary shown in detail dialog
- [x] Chat journal feedback shows detected mood, themes, and summary inline

### Iteration 4: Advanced Features (partial)
- [x] Chat history search (backend `search_messages()` + API endpoint)
- [x] Weekly summary page (`/summary`) with LLM-generated recap + stats
- [x] Summary nav item in sidebar

### Iteration 5: Deployment (partial)
- [x] GitHub Actions CI/CD (backend lint + test, frontend build on PR/push)

### Other Improvements
- [x] Embedding model upgraded to BAAI/bge-small-en-v1.5 (better accuracy than MiniLM)
- [x] Fixed all 22 tests (user_manager tests now pass with password param)
- [x] Merged journal save functions (chat path now runs full analysis like direct path)

---

## Next Up

### Priority 1: Safety & Trust

**LLM-based crisis detection**
Current regex patterns miss subtle signals ("I don't see a point in going on"). Add a secondary LLM classification check on every message before intent routing. Fast, zero-temperature call.

**Response feedback (thumbs up/down)**
Add feedback buttons on assistant messages. Store in DB. Use to identify weak prompts and improve over time. New table: `response_feedback` (message_id, rating, created_at).

### Priority 2: Engagement

**Onboarding flow**
First-time users see a welcome screen explaining features, with clickable example prompts ("How are you feeling?", "Give me a journaling prompt", "Log my therapy session"). Seed the system with initial context.

**Goal tracking**
New `goals` table. Preset templates: "Journal 3x per week", "Track mood daily", "Attend therapy weekly". Auto-compute progress from actual DB data. Progress bars on a new `/goals` page.

**Proactive check-ins**
Use the existing `reminders` table. Add UI to set check-in frequency. Show a banner on login: "You haven't journaled in 3 days — want to write something?" Browser notifications via service worker.

### Priority 3: Intelligence

**Semantic therapy recall**
Replace keyword matching in `find_relevant_therapy_sessions()` with embedding-based cosine similarity. "Overwhelmed at work" should match sessions about "workplace burnout." Use the BGE embedding model already loaded.

**Cross-session memory**
Maintain a synthesized "user profile" that carries across chat sessions — key patterns, ongoing concerns, therapy progress. Generated/updated by LLM after each session. Stored as a text field on the user record.

**Mood prediction**
With enough data, detect trends: "Your mood tends to drop on Sundays — want to plan something?" Simple rolling-average trend detection on mood_logs, surfaced as a chat prompt or dashboard alert.

**Relationship mapping**
Aggregate entities from journals to track people mentioned across entries. "Sarah comes up in 60% of your stress-related entries." Visualization on dashboard.

### Priority 4: Polish

**Therapist report export**
Generate a PDF report for sharing with a therapist: mood trends since last session, journal themes, chat conversation highlights, suggested discussion topics. Downloadable from the summary page.

**Journal analytics**
Sentiment trend chart (using scores we now collect), writing frequency heatmap (GitHub-contribution style), theme evolution over time, word count stats.

**Dark/light mode toggle**
Add theme switcher to settings page. Currently dark mode theme exists but no toggle UI. Store preference in localStorage.

**Voice input**
Web Speech API for chat input. One button in the chat footer — press to speak, release to send. Free, works in all modern browsers.

**Guided exercises**
Interactive breathing/grounding exercises in chat. Animated visual (expanding circle for 4-7-8 breathing). Timer-based steps instead of just describing the technique.

### Priority 5: Production Readiness

**JWT authentication**
Replace localStorage email with proper JWT tokens. `python-jose` for backend, `Authorization: Bearer` header on all API calls. Migration path: keep email fallback via `REQUIRE_AUTH` toggle.

**Docker Compose production**
`docker-compose.prod.yml` with PostgreSQL + pgvector (replacing SQLite + ChromaDB), Nginx reverse proxy, SSL, health checks.

**Vercel deployment**
Frontend deployment to Vercel. `next.config.ts` with `output: "standalone"`. Environment variable handling for `NEXT_PUBLIC_API_URL`.

**Rate limiting**
Add per-user rate limiting on API endpoints. LLM calls are expensive even on free tiers. Use `slowapi` or custom middleware.

**Data encryption**
Encrypt sensitive fields (journal entries, therapy notes) at rest. GDPR-compliant data deletion (full purge, not soft delete).

---

## Tech Debt

- [ ] `therapy_store.py` has imports below function definition (E402 lint errors)
- [ ] `save_journal_entry()` and `save_journal_entry_direct()` share duplicated logic — consider merging
- [ ] Chat search UI not yet built on frontend (backend endpoint exists)
- [ ] Knowledge base is global, not per-user — all users share the same PDFs
- [ ] No pagination on journal/therapy pages (uses offset/limit but no "Load More" UI)
