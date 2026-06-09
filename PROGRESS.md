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

## Session 003 — 2026-05-29 (continued same day)

**Type:** Bug fix / Dev environment clarification  
**Branch:** `claude/adhd-taskmanager-review-zRJtI`  
**Status:** Complete

### What Was Done

Short wrap-up session. Two items addressed:

**1. Windows dev testing confirmed viable**

Confirmed the app is fully testable on Windows in a regular browser without the Raspberry Pi kiosk environment. Setup steps agreed:
- `pip install -r requirements.txt`
- Copy `config.json.example` → `config.json`, set `setup_complete: true`
- `python app.py` → `http://localhost:5001`

What works on Windows: all routes, DB, AI features, Focus Mode, tree, Week View, Quick Add, Settings.  
What doesn't: Alexa/Voice Monkey (off by default anyway), audio autoplay, kiosk scaling.

**2. Display clarified: 14" touchscreen, not 7"**

The Pi is running a 14" touch panel (not the standard 7" Pi display). Resolution not yet confirmed but likely 1920×1080. The current CSS was written for 800×480 — font sizes, card dimensions, overlay sizing, and the tree SVG will all need reviewing against the actual resolution. This is deferred to next session once the resolution is confirmed.

**3. Bug fix: missing `requests` dependency**

`requirements.txt` was missing `requests`, which `llm_service.py` imports for all LLM API calls. Added `requests==2.31.0`.

### Files Changed This Session
- `requirements.txt` — added `requests==2.31.0`
- `PROGRESS.md` — this entry

### State at End of Session
- All v2 code pushed and ready to install
- Dev testing can proceed on Windows immediately
- **Blocked on**: 14" display resolution confirmation before CSS layout work
- Next session: confirm resolution → audit and fix font sizes, card dimensions, overlay sizing, tree SVG scale throughout all templates

---

## Session 004 — 2026-05-29 (continued same day)

**Type:** Display scaling fix  
**Branch:** `claude/adhd-taskmanager-review-zRJtI`  
**Status:** Complete — ready for user pull and test

### What Was Done

**Display confirmed: 14" 1920×1080 touchscreen**

User confirmed resolution. Identified and fixed two problems:

**1. scale.js and settings.html were inconsistent and wrong for 1920×1080**

- `scale.js` had: `{ small: 1.0, medium: 1.0, large: 1.39 }` — medium was no-op, large far too small
- `settings.html` had: `{ small: 1.0, medium: 1.39, large: 2.08 }` — different values, still wrong for 1080p

The correct zoom for 1920×1080 from the 800px-wide base design is **2.4** (1920÷800). At zoom 2.4:
- Virtual CSS viewport = 800px wide — matches the design exactly
- Virtual height = 1080÷2.4 = 450px — 30px less than the 480px design, flex adapts
- All overlays, card sizes, fonts, tree SVG all scale proportionally — no individual element changes needed

**2. Fixed values and labelled the button**

Both files now use: `{ small: 1.0, medium: 1.5, large: 2.4 }`.
LARGE button now sub-labelled "1920×1080" so it's obvious on first setup.
Removed dead medium-specific font override injection from scale.js (was overriding fonts separately but zoom already handles that).

**First-run instructions for 1920×1080:**
1. Open app → Settings → tap **LARGE** (1920×1080)
2. Setting persists in localStorage — all pages pick it up via scale.js on load

**Dev testing on Windows:**
- DevTools → device toolbar → 1920×1080 custom → Settings → LARGE

### Files Changed This Session
- `static/js/scale.js` — corrected zoom values, removed dead font injection
- `templates/settings.html` — matching zoom values, LARGE button labelled "1920×1080"
- `PROGRESS.md` — this entry

### State at End of Session
- All code pushed, ready to pull and test
- **Waiting for**: user to pull branch, install, run, and test on Windows (DevTools 1920×1080) or Pi
- Next session: runtime bug fixes from first real test

---

---

## Session 005 — 2026-06-01

**Type:** Bug fixes / Feature additions from first test  
**Branch:** `claude/adhd-taskmanager-review-zRJtI`  
**Status:** Complete — ready for re-pull and test

### What Was Done

Five issues raised after first Windows dev test. All fixed.

**Issue 1 — TONIGHT button now triggers Alexa briefing**

Tapping TONIGHT does two things: shows the overlay (unchanged) AND sends an evening VM briefing to `VM_DEVICE_BRIEFINGS`. Briefing speaks: how many tasks completed today (with names), how many still outstanding, and tomorrow's top-3 tasks with durations.

New `_send_tonight_vm()` helper handles the content. It is also called automatically by a new `run_evening_briefing()` background function which fires at the new `evening_briefing_time` setting (default 21:00) on configured briefing days.

**Issue 2 — Evening briefing time added to settings; both briefing times use clock picker**

`evening_briefing_time` field added to settings page, side-by-side with morning briefing time. Both have class `mask-time` so they open the clock picker when tapped (same as DND fields). Added to DB defaults (21:00) and to settings POST handler.

**Issue 3 — LLM and name removed from config.json.example**

`config.json.example` now contains only VM credentials, `setup_complete`, and gdrive fields. LLM setup and user name are settings-only. `get_user_name()` helper added to `app.py` — reads live from DB settings, falls back to `config.json USER_NAME` then `'Joe'`. All VM messages now use `get_user_name()` so name changes in settings take effect without restart.

**Issue 4 — AI Assistant expanded: Google + LlamaCPP, model dropdowns**

Providers: OPENAI, ANTHROPIC, GOOGLE, OLLAMA, LLAMACPP (5 buttons).

Cloud providers (OpenAI/Anthropic/Google): show model dropdowns pre-populated with common models, plus "Custom..." option that reveals a text input. Two hidden inputs (`llm_quick_model`, `llm_deep_model`) hold the actual submitted values, updated by JS before form submit.

Local providers (Ollama/LlamaCPP): show plain text inputs for model names, and a host field (reuses `llm_ollama_host` DB key). API key section hidden for local, host section hidden for cloud. Label dynamically changes ("OPENAI API KEY" / "GOOGLE API KEY" etc.).

`llm_service.py` extended with Google Gemini (REST API, system_instruction support) and LlamaCPP (OpenAI-compatible `/v1/chat/completions` endpoint). LLM help popup updated with Google and LlamaCPP instructions.

**Issue 5 — Numpad decimal fix + spinner arrows removed**

Numpad now uses a string buffer (`numpadBuffer`) instead of writing directly to `input.value` on every keypress. This fixes the decimal point resetting (browsers reject incomplete `type=number` values like `"5."`). Value is only written to the input on OK. `CLR` button replaced with `⌫` (backspace, deletes last character). Double-decimal prevented.

Number input spinner arrows hidden globally with CSS (`-webkit-appearance: none` + `appearance: textfield`) so tapping near the arrows no longer accidentally opens the numpad.

### Files Changed This Session
- `app.py` — get_user_name(), _send_tonight_vm(), run_evening_briefing(), evening_briefing_time default, settings POST, background loop, all VM messages use get_user_name()
- `llm_service.py` — Google Gemini + LlamaCPP providers
- `config.json.example` — removed LLM and USER_NAME fields
- `templates/settings.html` — evening briefing field, 5-provider AI section with model dropdowns, numpad buffer fix, spinner CSS, LLM help updated
- `PROGRESS.md` — this entry

### State at End of Session
- All changes pushed, ready for user re-pull and test
- Next session: runtime bugs from second test round

---

## Session 006 — 2026-06-02

**Type:** Bug fixes / LLM connectivity / Quick Add redesign  
**Branch:** `claude/adhd-taskmanager-review-zRJtI`  
**Status:** Complete — ready for re-pull and test

### What Was Done

**Fix 1 — LLM connection: TEST CONNECTION tested stale DB not live form**

Root cause: `fetch('/api/test_llm', { method: 'POST' })` sent no body. The endpoint read from the DB, so first-time users always tested empty/stale settings.

Fixed: `testLLM()` JS now sends all current form values (provider, quick_model, deep_model, api_key, ollama_host) as JSON. `/api/test_llm` endpoint accepts these as live overrides. `call_llm()` updated with `overrides` param that takes top precedence over DB and config.json.

**Fix 2 — LLM error messages now show the actual API error**

Previously all failures returned the same generic "Connection failed — check provider, model name, host/API key." The actual HTTP error (wrong key, bad model name, network error) was swallowed.

Fixed: `call_llm()` now catches `requests.exceptions.HTTPError` separately, extracts the error message from the JSON response body (works for OpenAI, Anthropic, Google formats), and stores it in module-level `_last_error`. `test_connection()` returns `_last_error` when set. `ConnectionError` (server unreachable) returns a distinct "Cannot reach provider" message.

Example: now returns "HTTP 401: invalid x-api-key" instead of generic failure.

**Fix 3 — API key whitespace stripping**

API keys and model names now stripped of leading/trailing whitespace in `call_llm()` before use. Paste-with-trailing-space was a likely silent failure cause.

**Fix 4 — LlamaCPP host auto-defaults to :8080**

When user selects LLAMACPP provider button in settings, the host field auto-changes from `:11434` to `http://localhost:8080` (and back to `:11434` when switching to OLLAMA). Only applies if the field contains the other provider's default port.

LlamaCPP blank model now defaults to `'local'` (server picks the loaded model) instead of bailing out with "no model" error.

**Fix 5 — Google and Anthropic model lists updated**

Google: gemini-3.5-flash, gemini-3.1-pro-preview, gemini-3-flash-preview, gemini-3.1-flash-lite, gemini-2.5-flash, gemini-2.5-flash-lite, gemini-2.5-pro  
Anthropic: claude-opus-4-8, claude-sonnet-4-6, claude-haiku-4-5-20251001 (fixed ordering/typo)

**Fix 6 — Complex task breakdown flow wired up (was completely missing)**

The three backend endpoints (`/api/breakdown/questions`, `/api/breakdown/complete`, `/api/breakdown/commit`) existed but were never called — `validateAndSubmit()` in add.html did a plain form submit regardless of the COMPLEX TASK toggle.

Fixed: `validateAndSubmit()` now intercepts when `is_complex` = 1 and runs a multi-step flow:
1. Fetches 5 yes/no questions from `/api/breakdown/questions`
2. Shows each question full-screen with YES/NO buttons (one at a time)
3. Calls `/api/breakdown/complete` with answers → LLM generates 3-7 subtasks
4. Shows subtasks preview with titles, durations, deadlines
5. SAVE THESE TASKS calls `/api/breakdown/commit` → creates parent task + all subtasks → redirects home

Three new modals added to add.html: loading spinner, question prompt, subtasks preview.

**Fix 7 — Quick Add redesigned for touchscreen (replaces textarea + PARSE WITH AI)**

Old approach: type a natural language paragraph, hit PARSE WITH AI, AI extracts fields. Impractical on a touchscreen without a keyboard.

New approach — touchscreen-first form:
- **TASK NAME**: text input
- **DEADLINE**: three toggle buttons (FIXED / FLEXIBLE / NO DATE) — same colour coding as rest of app
- **BY DATE**: date field using the same full-screen touch calendar (year → month → day) as the add task page. Hidden when NO DATE selected.
- **AT TIME**: time field using the same analog clock picker. Hidden when NO DATE selected.
- **DURATION**: six quick-tap buttons (15 / 30 / 45 / 60 / 90 / 120 min) + custom number input. AI ESTIMATE button fills in duration with LLM estimate + buffer.
- **SAVE TASK**: validates fields and posts directly to `/add` — no AI parsing required.

Date picker (year/month/day calendar) and clock picker (analog) added to index.html as `qa-touch-picker` and `qa-clock-picker` (prefixed to avoid collision with any future pickers on the page). Full JS for both pickers included. Click listeners attached at DOM load directly to the two input elements.

### Files Changed This Session
- `llm_service.py` — `_last_error` global, improved exception handling, `call_llm()` overrides + whitespace stripping, `test_connection()` returns real errors
- `app.py` — `/api/test_llm` accepts live JSON overrides, `force=True` on JSON parse
- `templates/settings.html` — `testLLM()` sends live form values, LlamaCPP auto-port-swap, updated model lists
- `templates/add.html` — complex task breakdown flow: `startBreakdownFlow()`, question modal, subtasks preview modal, `confirmBreakdown()`, `cancelBreakdown()`
- `templates/index.html` — Quick Add redesigned: form-based UI, date/clock pickers added (`qa-touch-picker`, `qa-clock-picker`), full picker JS, new CSS classes
- `PROGRESS.md` — this entry

### State at End of Session
- All changes pushed to branch
- User confirmed LlamaCPP connection worked
- Cloud providers (Google/Anthropic) need testing with live API keys
- Complex task breakdown and new Quick Add awaiting runtime test

---

## Session 007 — 2026-06-07

**Type:** New feature — Google Calendar integration  
**Branch:** `claude/adhd-taskmanager-review-zRJtI`  
**Status:** Complete — ready for OAuth setup and test

### What Was Done

Full Google Calendar + Google Tasks integration. Additive — the app works exactly as before; GCal sync is an enhancement.

**Architecture:**
- `gcal_service.py` (new) — all Google API interactions: OAuth2 token exchange/refresh, reading primary calendar busy slots, CRUD on Google Tasks
- `scheduler.py` (new) — pure scheduling algorithm: assigns tasks to first available slot between GCal appointments, respects daily_capacity, tightest deadline first
- `app.py` — DB migration (gcal_task_id, scheduled_start, scheduled_end on tasks), sync function, OAuth routes, completion hook, background thread integration
- `templates/settings.html` — Google Calendar section with connect/disconnect/sync-now UI

**OAuth flow:**
- Uses existing gdrive_client_id / gdrive_client_secret from config.json
- Scopes: calendar.readonly + tasks (read/write)
- Redirect URI: http://localhost:{port}/gcal_callback — works in Pi kiosk Chromium
- Tokens stored in settings DB (access_token, refresh_token, expiry)
- Auto-refresh when within 5 min of expiry
- `prompt=consent` ensures refresh_token is always returned

**Calendar reading:**
- Reads primary calendar events for next 21 days
- All-day events ignored (no time slot to conflict with)
- Busy slots returned as {date_str: [(start_naive_local, end_naive_local), ...]}

**Scheduling algorithm:**
- Sorts tasks by deadline ascending (tightest first = highest priority)
- For each task: iterates days from today to deadline
- Per day: work window = work_start_hour to work_start + capacity_hours
- Subtracts GCal busy slots + already-allocated slots from this run
- Assigns first gap >= task duration
- Backlog / no-deadline tasks skipped
- Status: 'scheduled' | 'unschedulable' | 'skipped'

**Google Tasks integration:**
- Creates/updates tasks in "ADHD Tasks" tasklist (created if absent)
- Title format: "Task Name [Mon 14:00-15:30]" — time embedded in title
- Updates title+due date if rescheduled (when slot changes)
- Marks as completed (status='completed') when task done in app — task kept for dopamine history
- gcal_task_id stored in tasks DB to link app tasks to GCal tasks

**Background sync:**
- `run_gcal_sync()` called from background_task_checker()
- Respects gcal_sync_interval_hours setting (default 24h)
- Module-level `_gcal_last_sync_attempt` tracks last run time
- SYNC NOW button in settings resets timer and forces immediate sync

**Conflict resolution:**
- On conflict (appointment moved into task slot): scheduler reassigns on next sync
- No manual confirmation needed — auto-reschedule per user request
- Unschedulable tasks (no slot before deadline): scheduled_start/end set to NULL; will show in next iteration

**Settings UI:**
- Status dot (green=connected+active, orange=connected+paused, grey=not connected)
- CONNECT GOOGLE CALENDAR button → /gcal_auth_redirect → Google OAuth → /gcal_callback
- SYNC NOW button (calls /api/gcal_sync_now, shows result)
- DISCONNECT button (clears tokens, disables)
- Sync interval (hours) and Work day start (hour) fields
- Success/error flash messages via query params

**New settings keys:**
- gcal_enabled: '0'/'1'
- gcal_sync_interval_hours: default '24'
- gcal_work_start_hour: default '9' (9 = 09:00)
- gcal_access_token, gcal_refresh_token, gcal_token_expiry, gcal_tasklist_id: managed by gcal_service

**Prerequisites for user:**
1. Google Cloud Console: enable Calendar API + Tasks API
2. Create OAuth 2.0 credentials (Web application type)
3. Add http://localhost:{port}/gcal_callback as Authorized Redirect URI
4. Client ID + secret already in config.json from GDrive setup (same project can be used)

### Files Changed This Session
- `gcal_service.py` — new: OAuth2, calendar reading, Google Tasks CRUD
- `scheduler.py` — new: time-slot scheduling algorithm
- `app.py` — set_setting(), DB migration (3 new task columns), gcal defaults, run_gcal_sync(), background thread, complete_task_internal GCal hook, 5 new routes, settings POST update
- `templates/settings.html` — Google Calendar section with status/connect/sync UI + JS
- `PROGRESS.md` — this entry

### State at End of Session
- All changes pushed to branch
- Scheduler tests pass (empty slots + busy block + two competing tasks)
- Awaiting: Google Cloud Console setup by user, first OAuth connect, first sync test

---

## Session 008 — 2026-06-07 (continued same day)

**Type:** Documentation update / Feature removal  
**Branch:** `claude/adhd-taskmanager-review-zRJtI`  
**Status:** Complete

### What Was Done

**1. Separate Calendar OAuth credentials (addendum to Session 007)**

A user scenario was identified: the GDrive account and Google Calendar account may belong to different Google accounts. The `gcal_service._get_client_credentials()` function was updated to check the DB for `gcal_client_id` / `gcal_client_secret` first, then fall back to `gdrive_client_id` / `gdrive_client_secret` from config.json. The settings UI has corresponding optional fields with a note explaining this.

**2. Daily capacity system removed**

The per-weekday capacity tracking system (Mon–Sun hours, capacity bar, TODAY chip, REBALANCE, week view capacity bars) was removed from all code per user decision. The system was over-engineered for the use case; Google Calendar integration provides real scheduling data, making the capacity estimation layer redundant.

Removed from app.py:
- `get_today_capacity()`, `get_day_capacity()`, `get_today_planned_hours()` functions
- `daily_capacity` and `capacity_overrides` table creation
- `cap_mon` through `cap_sun` defaults and seeding logic
- Capacity over-limit check in `add_task()`
- `today_cap`, `today_planned`, `cap_pct`, `tomorrow_cap` from `index()` route
- `/api/capacity`, `/api/capacity/update`, `/api/week_view`, `/api/rebalance/<day>`, `/api/rebalance/apply` routes
- `cap_*` keys from settings POST handler + daily_capacity sync block

Updated:
- `scheduler.py` — `daily_caps` dict replaced with `work_end_float` (default 17.0) parameter; scheduler now uses work_start to work_end window every day (GCal appointments carve out busy time)
- `run_gcal_sync()` — reads `gcal_work_end_hour` setting (default 17) instead of querying daily_capacity
- `tonight_api()` — removed `tomorrow_available_h` / `tomorrow_planned_h` from response
- `settings.html` — removed DAILY CAPACITY section; added WORK DAY ENDS field to GCal settings row
- `index.html` — removed cap-chip, WEEK VIEW button, capacity edit popup, rebalance confirm, all related CSS and JS

**3. BLUEPRINT.md and PROGRESS.md updated**

Both documents updated to reflect: 5 LLM providers, new Google Calendar integration section, updated Quick Add spec (form-based, not NLP), updated data model (GCal columns), updated architecture (gcal_service.py + scheduler.py), daily capacity marked as removed, mobile as next planned phase.

### Files Changed This Session
- `app.py` — daily capacity functions/routes/settings removed, scheduler call updated
- `scheduler.py` — `daily_caps` replaced with `work_end_float`
- `templates/settings.html` — DAILY CAPACITY section removed, work_end_hour added
- `templates/index.html` — capacity chip, week view, rebalance removed
- `BLUEPRINT.md` — major update to reflect all sessions 006–008 changes
- `PROGRESS.md` — this entry

### State at End of Session
- All changes pushed to branch
- Next session: Google Cloud Console OAuth setup by user + first GCal connect + sync test

---

## Session 009 — 2026-06-09

**Type:** Bug fixes — GCal sync timing and duplicate entries  
**Branch:** `claude/adhd-taskmanager-review-zRJtI`  
**Status:** Complete — ready for re-test

### What Was Done

Three GCal integration bugs found during first live test with real OAuth credentials.

**Bug 1 — Tasks only appeared in GCal after manual SYNC NOW**

Root cause: `run_gcal_sync()` was only called by the background thread (on its interval) and the manual SYNC NOW button. Adding a task did nothing to GCal until the next background cycle.

Fix: Added `_trigger_gcal_sync_async()` helper that resets `_gcal_last_sync_attempt = None` and launches `run_gcal_sync()` in a daemon thread. Called from `add_task()` immediately after `conn.commit()` when GCal is enabled. Tasks now appear in Google Tasks within seconds of being added.

**Bug 2 — Completing a task in the app did not mark it complete in GCal**

Root cause: `complete_task_internal()` only called `gcal_service.complete_task()` if the task already had a `gcal_task_id`. For newly added tasks (before their first sync), `gcal_task_id` was NULL so the completion was silently skipped.

Fix: Expanded the completion block to handle the no-ID case. If `gcal_task_id` is NULL but GCal is enabled, the function now creates the task in GCal and immediately marks it complete in one go. The `gcal_task_id` is saved to the DB so the record remains consistent.

**Bug 3 — Syncing via SYNC NOW created duplicate entries in Google Tasks**

Root cause: `conn.commit()` and `conn.close()` were at the end of the `try` block in `run_gcal_sync()`. If any exception occurred mid-loop (a GCal API error on one task, a bad date format, anything), the entire `try` block exited without committing. The GCal tasks HAD been created (those API calls already went out), but `gcal_task_id` was never written to the local DB. Next sync: `gcal_task_id` was still NULL → created again.

Fix:
1. Moved `conn.commit()` / `conn.close()` to a `finally` block so they always run regardless of exceptions.
2. Added an extra `conn.commit()` immediately after each successful `create_task()` call, so the `gcal_task_id` is persisted before processing the next task.

**Also fixed — work-hour removal (Session 008 addendum)**

The WORK DAY STARTS/ENDS settings were removed and the scheduler changed to use a 24-hour window. The numpad popup was added to the duration field in Add Task.

### Files Changed This Session
- `app.py`:
  - `run_gcal_sync()` — `conn` initialised before try block, `finally` ensures commit/close, immediate commit after each `create_task()`
  - `complete_task_internal()` — handles NULL `gcal_task_id`: creates+completes GCal task inline
  - `add_task()` — calls `_trigger_gcal_sync_async()` after saving
  - `_trigger_gcal_sync_async()` — new helper function
- `scheduler.py` — removed `work_start_float`/`work_end_float`; uses 00:00–23:59 full day (committed Session 008)
- `templates/settings.html` — work hour fields removed (committed Session 008)
- `templates/add.html` — numpad popup for duration field, spinner arrows hidden (committed Session 008)
- `PROGRESS.md` — this entry

### State at End of Session
- All fixes pushed to branch
- GCal OAuth successfully tested by user (Session 008)
- Duplicate entry bug fixed — re-test by clearing existing GCal Tasks duplicates and running SYNC NOW
- Immediate sync on add/complete ready to test

---

*Future sessions appended below*
