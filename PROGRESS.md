# ADHD Task Manager — Session Progress Log

This file is a chronological record of every development session. Its purpose is disaster recovery and continuity — if everything is lost, this file plus BLUEPRINT.md contains enough information to reconstruct the project from any point in time, by any engineer or AI agent.

---

## Session 001 — 2026-05-29

**Type:** Planning / Specification  
**Branch:** `claude/adhd-taskmanager-review-zRJtI`  
**Status:** Complete — no code written this session

### What Was Done

This was a full design and specification session. No code was written. The output is the `BLUEPRINT.md` file committed to the branch.

**Phase 1 — Brainstorm review**

A comprehensive brainstorm was conducted covering the competitive landscape (Motion, Tiimo, Amazing Marvin, Goblin Tools, Forest, Reclaim.ai, Structured, Focusmate), the neuroscience of ADHD (time blindness, working memory limits, dopamine deficit, transition costs, novelty requirements), and a full feature-by-feature breakdown of what the v2 overhaul should contain.

The user's key reactions from the brainstorm:
- Liked Forest's tree gamification but did not want to copy it — wanted it incorporated into the completion screen without making the app noisy
- Identified task initiation as a real gap in v1 — the app rewards completion but not starting
- Asked whether the LLM could replace the pre-written message banks for true randomisation
- Confirmed they want a drag-and-drop week view for rescheduling, not a full noisy calendar
- Confirmed they do not want traditional priority levels (High/Med/Low) — instead: Fixed deadline / Flexible deadline / No deadline

**Phase 2 — Spec Q&A (Round 1)**

The following items were agreed through structured Q&A:

| Feature | Decision |
|---|---|
| LLM providers | OpenAI, Anthropic, Local (Ollama) |
| LLM setup | API key, test connection, "?" help button |
| Task duration | Mandatory field, AI ESTIMATE button, far-right cell on card |
| ADHD buffer | +30% default, configurable, single buffered number, gamified as challenge |
| Focus Mode trigger | Tap task → popup "Working on this now?" YES/NO |
| Focus Mode time input | Pre-filled with buffered duration, editable |
| Break reminders | <30min=none; 30-60min=halfway; >60min=every 30min — Alexa + visual |
| Focus Mode hard stop | Escalating nag (same as deadline system) |
| Daily capacity | Per-weekday defaults in settings + "TODAY: Xh [edit]" chip on dashboard |
| Auto-rescheduling trigger | Automatic, but always confirm before moving tasks |
| Cascade order | No-deadline → Flexible → Fixed (Fixed never moves) |
| Complex task breakdown | COMPLEX toggle → AI Socratic Q&A (max 5 binary questions) |
| Evening briefing | On-demand only, TONIGHT button on dashboard |
| Task access beyond top 5 | Scroll below top 5, chunky scroll bars throughout |

**Phase 3 — Gap Analysis**

After the initial Q&A, a gap analysis was performed against the original brainstorm. 12 un-specced items were identified. The following were agreed as v2 (deferred): energy types, weekly planning ritual, emotional state check-in, body doubling, shame spiral/Reset Day, rotating background, micro-wins jackpot, mobile ambition.

**Phase 4 — Spec Q&A (Round 2 — Gap Closure)**

| Feature | Decision |
|---|---|
| Completion gamification | Keep fireworks → animated water drop → tree grows. 1 tree/week, decays when tasks undone, randomised structure weekly, full week = massive celebration |
| Task initiation | Engage sound + card pulse + LLM "First step: [micro-action]" shown 5s on Focus Mode screen |
| LLM messages | Fresh bank of 50 messages (25 nag, 25 praise) generated every Monday 2:00am, stored in DB |
| Week view | Separate screen, 7 capacity bars, REBALANCE on overloaded days, AI suggests move, user approves |
| Energy types | Deferred to v2 |
| Capacity bar | Hidden normally, yellow at 80%+, red when overloaded |
| Focus Mode sounds | All three: engage sound at start, 2-min transition warning, capacity alarm on overload |
| Backlog | No-deadline tasks ARE the backlog, filled into quiet days as reward after deadline tasks |
| Tone | Fixed split: brutal nags, warm praise — no user setting |
| Model config | Two slots: QUICK MODEL (estimates, message bank) + DEEP MODEL (breakdown, scheduling) |
| Natural language input | QUICK ADD button → LLM parses free text → pre-fills form → user confirms |
| One Task Mode | Full screen, auto-activates during Focus Mode — task name + timer + DONE/CANCEL |

**Phase 5 — Documentation**

`BLUEPRINT.md` written and committed — 11 sections, ~1,000 lines. Contains: project overview, hardware context, design philosophy, neuroscience rationale, full feature specs, data model (SQL), architecture overview, UI/UX principles, competitive landscape, v2 ideas.

### Files Changed This Session
- `BLUEPRINT.md` — created (1,023 lines)
- `PROGRESS.md` — created (this file)

### State at End of Session
- No code written
- Full specification agreed and documented
- Ready for implementation

---

*Future sessions appended below*

