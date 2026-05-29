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

## Session 002 — 2026-05-29 (continued same day)

**Type:** Full v2 Implementation  
**Branch:** `claude/adhd-taskmanager-review-zRJtI`  
**Status:** Complete — all core v2 code written and pushed

### What Was Done

Full v2 implementation across 6 files. No new spec decisions were made — all work was direct implementation of the agreed BLUEPRINT.md.

### Files Changed This Session

**`llm_service.py`** — NEW FILE (fully implemented)
- `call_llm(prompt, model_type, system_prompt)` — routes to OpenAI/Anthropic/Ollama
- `test_connection()` — connection test for settings page
- `estimate_duration(task_title, buffer_pct)` → (raw_mins, buffered_mins, rationale)
- `get_first_step(task_title)` → one-sentence physical micro-action
- `generate_message_bank()` → 25 nag + 25 praise messages for weekly DB bank
- `parse_natural_language_task(text)` → {title, deadline_date, deadline_time, deadline_type, duration_minutes}
- `rebalance_suggestion(day, week_tasks, daily_capacity)` → {task_id, task_title, move_to, reason}
- `breakdown_complex_task(task_title, deadline, answers)` → list of subtask dicts
- `_get_cfg()` reads from config.json first, then overlays DB settings table (so UI settings take precedence)

**`app.py`** — REWRITTEN
- New DB tables: `daily_capacity`, `capacity_overrides`, `focus_sessions`, `message_bank`, `weekly_tree`
- Migration: adds `duration_minutes`, `deadline_type`, `parent_task_id`, `buffer_applied` to existing tasks table
- Default settings: adhd_buffer_pct=30, cap_mon=6 through cap_sun=0
- Helper functions: `format_duration`, `get_buffer_pct`, `get_today_capacity`, `get_day_capacity`, `get_today_planned_hours`, `get_or_create_tree`, `grow_tree`, `get_message_from_bank`, `get_active_focus_session`
- Background thread extended: `maybe_generate_message_bank()` (Monday 2am), `maybe_reset_tree()`
- New routes: `/api/tree`, `/api/capacity`, `/api/capacity/update`, `/api/week_view`, `/api/rebalance/<day>`, `/api/rebalance/apply`, `/api/focus/start`, `/api/focus/end`, `/api/focus/break_reminder`, `/api/focus/expired`, `/api/estimate_duration`, `/api/test_llm`, `/api/quick_add_parse`, `/api/tonight`, `/api/breakdown/questions`, `/api/breakdown/complete`, `/api/breakdown/commit`
- `complete_task_internal()` — shared completion logic (used by `/complete/<id>` and `/api/focus/end`)
- Updated `/add` to handle `deadline_type`, `duration_minutes`, NO DEADLINE sentinel
- Updated `/edit/<id>` to handle `deadline_type`, `duration_minutes`
- Updated `/settings` GET/POST to handle LLM keys and daily capacity
- Updated `index()` to pass: `today_cap`, `today_planned`, `cap_pct`, `tree`, `active_focus`, `user_name`, `tomorrow_cap`
- `active_focus` has `elapsed_seconds` and `session_id` computed server-side before passing to template

**`config.json.example`** — updated with LLM provider fields

**`templates/add.html`** — REWRITTEN
- Deadline type selector: 3 big tap buttons (FIXED / FLEXIBLE / NO DEADLINE)
- Date/time wrapper hides when NO DEADLINE selected
- Duration field + AI ESTIMATE button (calls `/api/estimate_duration`)
- AI estimate info strip shows raw/buffered breakdown + rationale
- COMPLEX TASK toggle (hidden field `is_complex` for breakdown flow)
- Updated validation: skips date/time check when deadline_type='none'
- Years in picker extended to 2025-2030

**`templates/edit_task.html`** — REWRITTEN
- Deadline type selector with current value pre-selected
- Duration field
- Date/time hidden when NO DEADLINE selected

**`templates/settings.html`** — REWRITTEN
- Added AI ASSISTANT section: provider buttons (OPENAI/ANTHROPIC/OLLAMA), quick/deep model inputs, API key input (hidden for Ollama), Ollama host input, TEST CONNECTION button, ? help popup
- Added ADHD BUFFER % input
- Added DAILY CAPACITY grid (Mon-Sun hours)
- Added USER NAME field
- LLM provider selection shows/hides API key vs Ollama host dynamically

**`templates/index.html`** — MAJOR OVERHAUL
- Header: clock, capacity chip (TODAY: Xh/Xh, yellow at 80%+, red at 100%+), QUICK ADD / TONIGHT / WEEK VIEW / +ADD / ⚙️ / SILENCE buttons
- Top-5 task cards: FOCUS button (right side, pointer-events:auto), duration chip (far right)
- Queue section: scrollable list with chunky scrollbar (replaced fixed 5×2 grid)
- Weekly tree SVG (bottom-right, semi-transparent): procedural drawing per variant (oak/cherry/pine/willow/maple), scales with growth_level 0.0→1.0
- Overlays: Focus Popup, One Task Mode (OTM), Week View, Quick Add, Tonight, Capacity Edit, Rebalance Confirm
- Focus Mode timer: countdown, break reminders (halfway for <60min, every 30min for >60min), 2-minute warning, escalating nag after expiry
- OTM: LLM first-step text fades after 5s, timer color: green→yellow→orange→red
- Auto-resumes active focus session on page load (elapsed_seconds from server)
- Week View: 7-day capacity bars, REBALANCE button on overloaded days, calls AI for suggestion with user confirm
- Quick Add: text area → parse → show fields → save directly to /add endpoint
- Tonight: completed today, tomorrow tasks + capacity, backlog preview
- Drag-to-complete (smiley) preserved from v1

### Bug Fixes Applied During Implementation
1. `focus_end`: accepted 'complete' reason (JS) vs 'completed' (Python) — fixed to accept both
2. `renderTonight`: fixed field names `completed_today` and `tomorrow_available_h`
3. `renderWeekView`: fixed `day.day_abbrev` → `day.day`, `day.day_name` → `day.day` for rebalance API call
4. `endFocus`: fixed `d.completed` → `d.status === 'success'` to trigger fireworks after focus completion
5. `active_focus` template variable: `elapsed_seconds` and `session_id` computed in `index()` route before passing to template
6. `llm_service._get_cfg()`: reads DB settings first so UI-saved config takes precedence over config.json

### State at End of Session
- All v2 code implemented and pushed
- Ready for testing on device
- Next session: test on Raspberry Pi, fix any runtime bugs, verify AI integration

---

*Future sessions appended below*

