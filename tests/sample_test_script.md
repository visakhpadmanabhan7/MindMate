# MindMate — Sample Test Script

Register with email: `demo@mindmate.com`, password: `demo123`, name: `Alex`

Test each message below in the chat. Wait for a response before sending the next one.

---

## Day 1: First Contact

### General Chat
```
Hey, what can you do?
```
Expected: Feature overview, warm greeting. Intent: general.

### Mood — Negative (should trigger enrichment)
```
I've been feeling really anxious lately, especially about work deadlines
```
Expected: Mood logged as "anxious". If knowledge base has PDFs indexed, should see "What science says" section with CBT techniques.

### Journal Entry via Chat
```
Today was overwhelming. Had three back-to-back meetings, my manager criticized my presentation in front of everyone, and I skipped lunch. I feel like I'm not good enough for this role. The only bright spot was a call with my friend Sarah who reminded me I've handled worse.
```
Expected: Entry saved. Response shows:
- Mood detected: overwhelmed or stressed
- Themes: work pressure, self-doubt, social support
- Summary: one-line synthesis
- Entry appears on /journal page with colored border

### Journaling Prompt Request
```
Give me a journaling prompt about dealing with criticism
```
Expected: A reflective question (not an entry save). Intent: journal, tool_class: prompt_request.

---

## Day 1: Therapy Session

### Log Therapy Session via Chat
```
Here are my therapy notes from today: We talked about my imposter syndrome at work. My therapist said it's common in high achievers and we explored where it started — probably from my dad always saying "you can do better." We practiced cognitive restructuring: identifying the automatic thought ("I'm not good enough"), finding evidence against it, and replacing it with a balanced thought. Homework: write down 3 accomplishments each evening this week. Techniques used: CBT cognitive restructuring, thought records.
```
Expected: Parsed into structured session:
- Issues: imposter syndrome, childhood patterns
- Learnings: about cognitive restructuring, origin of beliefs
- Action items: write down 3 accomplishments each evening
- Techniques: CBT cognitive restructuring, thought records
- Appears on /therapy page in timeline

---

## Day 2: Building History

### Morning Mood
```
Woke up feeling tired but okay. Didn't sleep well, kept thinking about that meeting.
```
Expected: Mood: tired. Passive detection, no explicit mood logging.

### Journal Entry
```
I tried the homework from therapy — wrote down 3 things I did well today: 1) Finished the quarterly report ahead of deadline 2) Helped a junior colleague debug their code 3) Spoke up in the team standup even though I was nervous. It felt weird at first but by the third one I actually felt a small sense of pride.
```
Expected: Saved with mood: hopeful or grateful. Themes: therapy homework, accomplishments, self-recognition.

### Positive Mood (should NOT trigger enrichment)
```
Actually feeling pretty good right now! The accomplishments exercise is working.
```
Expected: Mood logged as happy/hopeful. Warm response. NO "Based on your history" or "What science says" — enrichment only triggers for negative moods.

---

## Day 3: Testing Cross-Reference

### Anxiety Returns (should trigger split response with history)
```
I'm anxious again. Have another presentation tomorrow and I keep imagining my manager criticizing me in front of everyone again.
```
Expected: Split response:
- "Based on your history" should reference: the previous journal about the manager criticism, the therapy session about imposter syndrome and cognitive restructuring, the mood pattern (anxious multiple times)
- "What science says" should pull CBT techniques from knowledge base

### Therapy Prep
```
I have therapy tomorrow, can you help me prepare?
```
Expected: Summary of what happened since last session — mood trends, journal themes, unresolved action items, suggested topics.

### Pattern Analysis
```
What patterns do you see across my therapy sessions?
```
Expected: Cross-session analysis (only 1 session so far, but should reference it).

---

## Day 4: More Data Points

### Stressed Again
```
Work is killing me. Three people quit this month and I'm picking up all their work. I don't even have time to eat properly.
```
Expected: Mood: stressed. Enrichment should fire. History section should now have richer data to synthesize.

### Journal — Relationship Entry
```
Had a long talk with my partner tonight about how work has been affecting us. They said I've been distant and irritable. I know they're right but it made me defensive. We agreed to have a phone-free dinner every night. I want to be better at this.
```
Expected: Mood: sad or guilty. Themes: relationship conflict, work-life balance, communication. Entities: partner.

### Second Therapy Session via Chat
```
Therapy session notes: Discussed how work stress is spilling into my relationship. My therapist introduced the concept of "stress containers" — how we all have a finite capacity and when work fills it up, there's no room for patience at home. We talked about boundary setting at work: learning to say no, delegating more, and not checking email after 7pm. Also revisited the accomplishments exercise — I've been doing it most days. Action items: set an email boundary this week, practice saying "I need to think about that" before committing to new tasks.
```
Expected: Session #2 logged. Parsed correctly with issues, learnings, action items, techniques.

---

## Day 5: Testing Remaining Features

### Self-Care Advice
```
What are some good breathing techniques for when I feel overwhelmed?
```
Expected: RAG-powered response from knowledge base PDFs with citations and page numbers. Intent: selfcare, tool_class: advice.

### Explicit Mood Log
```
I feel calm today, 7/10
```
Expected: Mood: calm. Logged as explicit source.

### General Conversation
```
Thanks for being here. It helps to have somewhere to put all this.
```
Expected: Warm response. Intent: general. Possibly mood: grateful (passive detection).

---

## Page-by-Page Verification

### /dashboard
Check:
- [ ] Line chart shows mood dots colored by mood (green=happy, red=angry, amber=anxious)
- [ ] Gradient fill under the line
- [ ] Pie chart shows mood distribution with mood colors
- [ ] Stat cards: Total Entries, Streak (should be 4-5 days), Most Common mood, Sources (Chat %, Journal %)
- [ ] Source labels show text ("Chat 50%") not just icons
- [ ] Click a dot → detail panel shows source content
- [ ] Recent moods section with colored badges

### /journal
- [ ] Entries have mood-colored left border
- [ ] Theme cloud shows weighted sizes (bigger = more frequent)
- [ ] Click theme to filter entries
- [ ] Search works
- [ ] Click entry → detail dialog with summary (italic, top), content, themes, entities
- [ ] Sentiment dot (green/amber/red) on entry cards
- [ ] Edit entry → re-runs analysis
- [ ] Delete entry → confirmation → toast "Entry deleted"

### /therapy
- [ ] Timeline layout with numbered circle badges connected by vertical line
- [ ] Session #1 and #2 visible with all structured fields
- [ ] Action items show colored bullet dots
- [ ] "Log Session" button → form → save → toast "Session logged"
- [ ] Edit session → save → toast "Session updated"

### /summary
- [ ] Stats row: mood entries count, journal entries count, therapy sessions count
- [ ] LLM-generated summary covering mood trends, journal highlights, therapy progress
- [ ] Regenerate button works
- [ ] Loading state with spinner

### /knowledge
- [ ] Upload a PDF → progress bar → toast "Document indexed"
- [ ] Document list with gradient icons, size, chunk count
- [ ] Search → results with highlighted query matches and relevance %
- [ ] Delete document → confirmation → toast "Document deleted"

### /chat
- [ ] Session sidebar (desktop) with list of conversations
- [ ] LLM-generated session titles (not truncated text)
- [ ] New Chat button creates fresh session
- [ ] Switch between sessions loads correct messages
- [ ] Delete session with confirmation
- [ ] Bot/User avatars on messages
- [ ] Markdown rendering in assistant messages (bold, lists, headings)
- [ ] Typing indicator (3 bouncing dots)
- [ ] Timestamps appear on hover
- [ ] Edit button appears on user messages (hover)
- [ ] Toast notifications on errors

### /settings
- [ ] Profile card with avatar, email
- [ ] Export data button → toast "Download started"

---

## Edge Cases

### Empty State
Register a new user and visit each page before sending any messages. All should show friendly empty states, not errors.

### Crisis Detection
```
I want to kill myself
```
Expected: IMMEDIATE crisis response with 988 and 741741. No LLM processing of the content. No mood logging.

```
I've been thinking about self-harm
```
Expected: Same crisis response.

```
I'm worried about my friend who mentioned suicide
```
Expected: This SHOULD trigger crisis (contains "suicide"). Current regex-based detection will catch it.

### Long Messages
```
Paste a 500+ word journal entry to test that analysis handles long content and the UI doesn't break.
```

### Special Characters
```
Today I felt 😊 but also a bit 😰. Work was "fine" — if you can call it that. Temperatures hit 30°C & I couldn't focus.
```
Expected: Should handle emojis, quotes, ampersands, special chars without breaking.

### Rapid Messages
Send 5 messages quickly without waiting for responses. The UI should queue them properly without duplicate messages or state corruption.
