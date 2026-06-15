# ADHD Task Manager

A neurologically-informed, kiosk-mode task manager built for a Raspberry Pi touchscreen. It is not a general-purpose productivity app — it is an always-on, ambient externalisation of executive function for ADHD brains, converting abstract deadlines into visceral, spatial urgency through shrinking progress bars, colour, sound, and escalating Alexa voice nags. It is a Python/Flask web app backed by SQLite, with an LLM-wired scheduling/breakdown engine and two-way Google Calendar/Tasks sync.

> The core app works fully offline. The LLM, Alexa voice, and Google Calendar layers are all optional enhancements — basic task management (add, complete, view, nag, celebrate) never depends on them.

For the full design rationale and neuroscience behind every decision, see **[BLUEPRINT.md](BLUEPRINT.md)**. For the chronological build log, see **[PROGRESS.md](PROGRESS.md)**.

---

## Key Features

- **Top-5 dashboard** — the five most urgent tasks shown as cards ordered by deadline, each with a progress bar that shrinks as the deadline approaches. Remaining tasks live in a scrollable queue below.
- **Focus Mode / One Task Mode** — tap a task to start a full-screen countdown for its allocated time. The rest of the board disappears so nothing competes for attention.
- **Task initiation trigger** — on Focus Mode start, an LLM "first step" micro-prompt + engage announcement fire, providing the dopamine nudge needed to actually begin.
- **Anti-hyperfocus nudges & break reminders** — periodic break/stretch reminders during long sessions, a 2-minute transition warning before time runs out, and an escalating nag if the timer expires.
- **Duration field + ADHD buffer** — every task carries a work-duration estimate. An **AI ESTIMATE** button asks the LLM for a duration, then applies a configurable buffer (default +30%) to correct for chronic ADHD time-underestimation.
- **Complex task breakdown** — flag a task as COMPLEX and the AI asks up to 5 task-specific clarifying questions, then generates a sequenced set of editable subtasks (each with its own duration and scheduled slot) before committing them.
- **Quick Add** — a touchscreen-native capture form (text name + FIXED/FLEXIBLE/NO DATE toggle + touch calendar + analog clock picker + quick-tap durations), no OS keyboard required.
- **Auto-scheduling engine** — `scheduler.py` places tasks into gaps between real Google Calendar appointments, tightest deadline first, and writes the resulting slots back to the dashboard and to Google Tasks.
- **Google Calendar / Tasks integration** — reads the primary calendar (FreeBusy) to find busy slots, writes scheduled tasks to an "ADHD Tasks" tasklist with times embedded in the title, and marks them complete when done in-app.
- **LLM message bank** — a fresh bank of 50 messages (25 brutal nags, 25 warm praise) regenerated weekly (Monday ~2am) to prevent habituation. Falls back to extensive built-in message lists when no LLM is configured.
- **Celebration finale + weekly tree** — completing a task triggers a full-screen celebration and grows a procedural SVG "weekly tree" (oak / cherry / pine / willow / maple, randomised each week) that fills the dashboard background.
- **Alexa voice nags (Voice Monkey)** — escalating verbal alerts at 30 min, 15 min, deadline, and beyond, plus morning and on-demand evening briefings.
- **Recurring tasks** — template-based recurring tasks so the board is never blank.
- **Do Not Disturb & Silence** — DND time window plus a manual silence toggle to kill all audio during meetings or sensory overload.
- **Mobile / remote access** — reachable from a phone over Tailscale; the dashboard adapts when a mobile user-agent is detected.

---

## Architecture

### Backend (Python / Flask)

| File | Responsibility |
|---|---|
| `app.py` | Main Flask app: routes, SQLite schema/migrations, background worker thread, Focus Mode, weekly tree, message bank, Voice Monkey, briefings, GCal sync orchestration. |
| `llm_service.py` | LLM wrapper for 5 providers (OpenAI, Anthropic, Google Gemini, Ollama, LlamaCPP). Duration estimates, first-step prompts, weekly message bank, NL parsing, complex-task questions + breakdown. Reads config from `config.json` then overlays DB settings; surfaces real API errors; degrades gracefully when unavailable. |
| `gcal_service.py` | Google OAuth2 (exchange/refresh), Calendar FreeBusy reading with timezone handling, and Google Tasks CRUD. Supports separate OAuth credentials for Calendar vs Google Drive. |
| `scheduler.py` | Pure scheduling algorithm — sorts tasks by deadline, fills gaps between busy slots, never schedules into the past. Returns `scheduled` / `unschedulable` / `skipped` per task. |
| `templates/` | Jinja templates: `index.html` (dashboard + Focus Mode + Quick Add overlays + tree), `add.html`, `edit_task.html`, `settings.html`, `edit_list.html`, `manage_recurring.html`, `recovery.html`, setup screens. |
| `static/` | CSS / JS, including `scale.js` for kiosk display scaling. |

A background thread (`background_task_checker`) runs every 60s to fire deadline nags, briefings, recurring-task generation, weekly message-bank generation, tree upkeep, and Google Calendar sync. It is guarded with `WERKZEUG_RUN_MAIN` so it only starts in the worker process under the Flask reloader.

### Data model (SQLite — `tasks.db`)

- **`tasks`** — title, deadline, status, `duration_minutes`, `deadline_type` (`fixed` / `flexible` / `none`), `parent_task_id`, `buffer_applied`, `gcal_task_id`, `scheduled_start`, `scheduled_end`. No-deadline tasks use a sentinel deadline and act as the backlog.
- **`recurring_templates`** — recurring task definitions.
- **`settings`** — key/value config (LLM provider/models/key, ADHD buffer %, briefing times, DND window, GCal tokens & interval, port, etc.).
- **`focus_sessions`** — Focus Mode session log (task, start, planned minutes, end reason).
- **`message_bank`** — weekly LLM-generated nag/praise messages.
- **`weekly_tree`** — per-week tree variant, growth level, completion count.

---

## Setup & Installation

**Requirements:** Python 3 (3.10+ recommended) and the packages in `requirements.txt` (Flask, requests, etc.).

```bash
git clone https://github.com/TheSharmanator/adhdtaskmanager.git
cd adhdtaskmanager
pip install -r requirements.txt
```

Create your config from the example (or complete it via the `/setup` flow on first launch):

```bash
cp config.json.example config.json
```

Run the app:

```bash
python app.py
```

It serves on **`http://localhost:5001`** (host `0.0.0.0`, so it is reachable on the local network and over Tailscale). The port is read from the `port` setting and defaults to `5001`.

### First run

On first launch, if `setup_complete` is false you are redirected to **`/setup`**, which asks whether you want Google Drive backup:

- **No backup** → marks setup complete and goes to the dashboard.
- **Backup** → `/setup_oauth` collects a Google Drive OAuth client ID/secret, stores them in `config.json`, and completes setup.

`config.json` is gitignored — only `config.json.example` is committed.

### Kiosk mode

The app is designed to run permanently full-screen on the Pi's 14" 1920×1080 touchscreen via Chromium kiosk mode. In Settings, choose the **LARGE (1920×1080)** screen-size option so the layout scales correctly. A typical launch command:

```bash
chromium-browser --kiosk --noerrdialogs --disable-infobars http://localhost:5001
```

The server and browser can both be launched from the Pi's autostart file so the device boots straight into the board.

---

## Configuration

All runtime configuration is in **Settings** (gear icon) except Voice Monkey credentials, which live in `config.json`.

### Voice Monkey (Alexa)

`config.json` holds the Voice Monkey token, alert/briefing device names, and language. Set `"VM": true` to enable. Used for nags, briefings, and Focus Mode announcements. When disabled, in DND, or in Silence mode, all audio is suppressed. (Pairing a Voice Monkey virtual device to an Alexa routine is required — see the Voice Monkey docs.)

### LLM provider

In Settings → AI Assistant, pick one of **OpenAI / Anthropic / Google / Ollama / LlamaCPP**. Cloud providers take an API key and model dropdowns (with a "Custom…" option); local providers take a host (`IP:port`) and model names. Two model slots are configured:

- **QUICK MODEL** — fast operations: duration estimates, message bank, first-step prompts, breakdown questions.
- **DEEP MODEL** — heavier operations: complex-task breakdown.

A **TEST CONNECTION** button fires a live call using the current form values and surfaces the real API error if it fails. If no LLM is configured, AI features degrade silently and the built-in message banks are used.

### Google Calendar OAuth

In Settings → Google Calendar Sync:

1. In Google Cloud Console, enable the **Calendar API** and **Tasks API** and create OAuth 2.0 (Web application) credentials.
2. Add `http://localhost:{port}/gcal_callback` as an authorised redirect URI.
3. Click **CONNECT GOOGLE CALENDAR** to authorise (scopes: `calendar.readonly` + `tasks`).
4. Optionally configure the sync interval; **SYNC NOW** forces an immediate sync.

By default this reuses the Google Drive OAuth client from `config.json`; optional separate `gcal_client_id` / `gcal_client_secret` settings let Calendar live in a different Google account. Tokens are stored in the settings table and auto-refresh near expiry.

### Other settings

ADHD buffer %, morning/evening briefing times and days, DND window, nag interval, progress-bar time scale, user name, and screen-size multiplier are all configurable in Settings.

---

## Mobile access

The kiosk runs on the Pi; a phone reaches it over **Tailscale** (a private mesh VPN — no port forwarding). Install Tailscale on both the Pi and the phone, then browse to the Pi's Tailscale IP plus the port, e.g. `http://100.x.x.x:5001`.

The dashboard detects mobile user-agents and adapts. A dedicated, fully mobile-optimised interface (task list with done/edit, Quick Add and add-with-AI, and a celebration screen) is an active development phase being built/refined separately — see BLUEPRINT.md §11.8. Because Google Calendar sync keeps the schedule synced, the mobile view primarily needs to display and quickly manage tasks.

---

## Usage

Day to day: glance at the always-on board to see your top-5 urgent tasks. Tap **QUICK ADD** to capture a task in a few taps. Tap a task and confirm **"Working on this now?"** to drop into Focus Mode — the screen clears to a single countdown, the AI gives you a concrete first step, and break/transition reminders keep you on track. Complete a task (drag the smiley, or **DONE** in Focus Mode) to trigger the celebration and grow the weekly tree. Overdue tasks flash and escalate Alexa nags until handled; use **SILENCE** or the DND window to mute. Tap **TONIGHT** for an on-demand evening briefing of what you finished and what's coming tomorrow.

---

## Further reading

- **[BLUEPRINT.md](BLUEPRINT.md)** — master design document: philosophy, neuroscience, full feature specs, data model, architecture.
- **[PROGRESS.md](PROGRESS.md)** — session-by-session implementation log.
</content>
