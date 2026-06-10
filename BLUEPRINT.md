# ADHD Task Manager — Master Blueprint
**Version:** 2.0 (In Development)  
**Status:** Actively being built — see PROGRESS.md for session-by-session implementation log  
**Last Updated:** 2026-06-07  
**Purpose:** Complete reference document for any engineer or AI agent implementing this system. Contains full project context, design philosophy, agreed feature specifications, data model, architecture, and v2 ideas. Do not begin implementation without reading this document in full.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Hardware & Deployment Context](#2-hardware--deployment-context)
3. [Core Design Philosophy](#3-core-design-philosophy)
4. [What Already Exists (v1)](#4-what-already-exists-v1)
5. [The Neuroscience Behind Every Decision](#5-the-neuroscience-behind-every-decision)
6. [Agreed Feature Specifications (v1 Overhaul)](#6-agreed-feature-specifications-v1-overhaul)
   - 6.1 [LLM Integration & Setup](#61-llm-integration--setup)
   - 6.2 [Task Duration Field & AI Estimation](#62-task-duration-field--ai-estimation)
   - 6.3 [ADHD Buffer System](#63-adhd-buffer-system)
   - 6.4 [Focus Mode](#64-focus-mode)
   - 6.5 [One Task Mode](#65-one-task-mode)
   - 6.6 [Anti-Hyperfocus System](#66-anti-hyperfocus-system)
   - 6.7 [Task Initiation Trigger](#67-task-initiation-trigger)
   - 6.8 [Completion Screen & Weekly Tree](#68-completion-screen--weekly-tree)
   - 6.9 [Dashboard Layout Changes](#69-dashboard-layout-changes)
   - 6.10 [Day Capacity System](#610-day-capacity-system)
   - 6.11 [Auto-Scheduling Engine](#611-auto-scheduling-engine)
   - 6.12 [Week View Screen](#612-week-view-screen)
   - 6.13 [Complex Task Breakdown](#613-complex-task-breakdown)
   - 6.14 [Quick Add (Touchscreen Form)](#614-quick-add-touchscreen-form)
   - 6.20 [Google Calendar Integration](#620-google-calendar-integration)
   - 6.15 [LLM Message Bank](#615-llm-message-bank)
   - 6.16 [Evening Briefing](#616-evening-briefing)
   - 6.17 [Backlog (No-Deadline Tasks)](#617-backlog-no-deadline-tasks)
   - 6.18 [Sound Design](#618-sound-design)
   - 6.19 [Settings Overhaul](#619-settings-overhaul)
7. [Data Model](#7-data-model)
8. [Architecture Overview](#8-architecture-overview)
9. [UI/UX Principles](#9-uiux-principles)
10. [Competitive Landscape](#10-competitive-landscape)
11. [V2 Ideas (Deferred)](#11-v2-ideas-deferred)

---

## 1. Project Overview

The ADHD Task Manager is a purpose-built, kiosk-mode task management board running on a Raspberry Pi with a touchscreen. It is not a general-purpose productivity app. It is a neurologically-informed externalisation of executive function, designed for a single user (or small group of neurodivergent users) who need aggressive, sensory-driven task management.

The app runs as a Python/Flask web server. It is displayed permanently on a touchscreen in kiosk mode — always on, always visible, ambient in the room. The user interacts with it passively (glancing at it) and actively (touching the screen to add, complete, or manage tasks).

**The core problem it solves:** ADHD brains experience time as binary — NOW and NOT NOW. Abstract deadlines feel unreal until they're imminent. The app converts abstract time into visceral, spatial, always-visible urgency through progress bars, colour, sound, and aggressive Alexa alerts.

**What makes it unique in the market:** No competitor combines all of:
- Kiosk/ambient always-on display
- Alexa voice integration for escalating nags
- ADHD-specific visual urgency system (shrinking progress bars)
- Celebration finale with randomised audio/visual rewards
- LLM-wired scheduling engine
- Neuroscience-backed design philosophy throughout

---

## 2. Hardware & Deployment Context

- **Primary device:** Raspberry Pi 4B with touchscreen
- **Display mode:** Chromium in kiosk mode, locked to `http://[pi-ip]:5001`
- **Always on:** The screen is ambient — always visible in the user's environment
- **Touch input:** Fat-finger friendly. All interactive elements must be large. Chunky scroll bars throughout. Minimum tap target size enforced.
- **Audio:** Alexa speaker via Voice Monkey API integration
- **Network:** Local network. Tailscale used for remote access (simple add/complete tasks interface available remotely)
- **Backend:** Python/Flask, SQLite database (`tasks.db`)
- **LLM connectivity:** Remote API calls to OpenAI/Anthropic/Google, OR local Ollama/LlamaCPP instance running on a separate powerful desktop machine (NOT on the Pi — it cannot run models locally). Local models are accessed over the local network.
- **No internet dependency for core function:** The app must remain functional if the LLM is unavailable. LLM is an enhancement, not a dependency for basic task management.
- **Remote access:** Tailscale used for remote access. A mobile-friendly simplified interface is the next planned phase after the kiosk v2 is stable.
- **Google Calendar:** Primary calendar (read) used to find busy slots for scheduling. Google Tasks (write) receives scheduled tasks with times in their titles. Can run under a different Google account than Google Drive backup.

---

## 3. Core Design Philosophy

Every design and feature decision must be measured against these principles. If a proposed feature violates them, it should be reconsidered or cut.

### 3.1 Zero Friction for Core Actions
Adding a task, completing a task, and starting Focus Mode must never require more than 3 taps. Any flow that requires navigation, explanation, or multi-screen journeys is wrong.

### 3.2 No Information Held in Working Memory
Every piece of data the user needs must be visible on screen. The app externalises working memory — it does not ask the user to remember things between screens. The top-5 task limit exists for this reason. LLM flows must never ask the user to hold context between steps.

### 3.3 Reward at Start AND End
The existing app rewards completion (fireworks, applause, celebration). The overhaul adds a reward at initiation too (engage sound, LLM micro-prompt). Dopamine deficit causes task initiation failure — the brain needs a trigger to start, not just a promise of reward at the end.

### 3.4 Aggressive by Design
The escalating nag system, the brutal nag messages, the flashing overdue states — these are intentional. They create a physiological "itch" that must be scratched. This is not cruelty; it is the only tone that cuts through the ADHD attention filter.

### 3.5 Tone Split: Brutal to Nag, Warm to Praise
Nag messages (overdue, reminder, escalation) are brutal and snarky (British wit). Completion praise messages are warm and celebratory. This split is fixed — not a user setting. The contrast between the two tones IS the reward mechanism.

### 3.6 Novelty Prevents Habituation
ADHD brains habituate rapidly to predictable stimuli — a pattern becomes invisible. Every reward and message must feel unpredictable. This is why the celebration themes are randomised, why the LLM generates fresh message banks weekly, and why the completion tree structure changes every week. Randomisation is a functional requirement, not a cosmetic one.

### 3.7 Accessibility First
This is an ADHD app. Its users likely have other neurodivergent traits. All UI elements must be large, high contrast, and touch-friendly. Chunky scroll bars. Large buttons. Internal keyboard (no OS keyboard disrupting layout). No small tap targets.

### 3.8 Kiosk Context
The app is always visible in the room. It is ambient. Design decisions must account for the fact that the user is sometimes not actively using it — they are glancing at it from across the room. The most important information (overdue state, today's top task, capacity status) must be scannable at a glance from several metres away.

---

## 4. What Already Exists (v1)

Do not rebuild what already works. This section describes the existing system so implementers know what to build on, not replace.

### 4.1 Dashboard
- Top 5 tasks displayed as task cards, ordered by deadline (soonest first)
- Each card has a progress bar that shrinks as the deadline approaches — converting abstract time into spatial urgency
- Smiley face icon draggable onto a task to mark it complete (desktop). On mobile, a DONE button.
- Task cards show: task title, deadline date/time
- Settings accessible via gear icon

### 4.2 Urgency Engine (Post-Deadline / Overdue State)
- Once a deadline passes, the task enters OVERDUE state
- Task bar flashes/pulses in high-contrast colour (red/yellow) — creates visual "itch"
- Alexa integration triggers escalating verbal nags at intervals until task is handled
- The nag escalates in frequency and intensity over time

### 4.3 Celebration Finale (Task Completion)
- Completing a task triggers a full-screen celebration
- Randomised visual themes (fireworks, confetti, matrix, glitch, etc.)
- Randomised audio: Alexa plays from a bank of praise messages — ranging from warm encouragement to snarky British wit
- Currently 5+ visual themes — target is 15+ after overhaul

### 4.4 Morning Briefing
- Scheduled Alexa announcement summarising the day's tasks
- Configurable time in Settings
- Already working via Voice Monkey integration

### 4.5 Nuke Button
- Emergency silence: kills all flashing and audio for a configurable snooze period
- For use during meetings, overstimulation, or sensory overload

### 4.6 Recurring Tasks
- Template-based recurring task system
- Look-ahead system: generates next iteration automatically on completion or time trigger
- Ensures the board is never blank

### 4.7 Settings
- Alexa volume, urgency window, nuke duration, morning briefing time
- Config stored in SQLite settings table
- Screen size multiplier (Small / Medium / Large) stored in localStorage

### 4.8 Do Not Disturb Mode
- DND silences all alerts
- 3-tap screen wake: tap screen 3 times to temporarily wake the app during DND
- Auto-returns to DND after 2 minutes of inactivity

### 4.9 Mobile / Remote View
- Stripped-down interface accessible via Tailscale for remote task management
- Basic add/complete tasks remotely — not a full mobile experience

---

## 5. The Neuroscience Behind Every Decision

These are not UX preferences. They are physiological realities that every feature decision must respect.

**1. Time exists in two states: NOW and NOT NOW.**
Not "soon." Not "tomorrow." Binary. Deadlines only feel real when they're imminent. The progress bar fights this by converting time into space. Task duration (new) makes the NOW feel of the work itself visceral, not just the deadline.

**2. Working memory holds ~3-4 chunks maximum.**
Every piece of information the user holds in their head is a cognitive tax. The top-5 limit exists for this. The LLM breakdown flow is capped at 5 binary questions for the same reason. Confirmation dialogs must be single questions with clear options, not walls of text.

**3. Dopamine deficit causes initiation failure, not laziness.**
The brain won't start a task it can't see a reward for. The existing app provides reward at completion. The overhaul adds an initiation trigger: engage sound + LLM micro-prompt at Focus Mode start. This closes the motivation loop at both ends.

**4. ADHD brains underestimate task duration by 30-100% consistently.**
This is physiological, not a skill gap. The ADHD buffer (+30% default) corrects for this. Transparency about the buffer is important — the user should understand why their time estimate has been increased. Framing it as a game ("can I beat the clock?") turns the buffer into motivation rather than insult.

**5. Transitions are neurologically costly.**
Switching between tasks burns disproportionate cognitive energy. The 2-minute transition warning before Focus Mode ends gives the brain time to prepare. The anti-hyperfocus break reminders prevent the opposite problem — getting so locked in that the transition becomes a shock.

**6. Novelty resets dopamine.**
When a pattern becomes predictable it becomes invisible. The rotating LLM message bank (regenerated weekly), the randomised celebration themes, the randomised weekly tree structure — all exist to prevent habituation. Randomisation is a functional necessity, not decoration.

**7. ADHD energy is not constant.**
The scheduling engine must respect daily capacity — not just total tasks. Overloading a day is worse than leaving tasks for tomorrow. The capacity bar, capacity alarm, and week view all exist to prevent silent over-commitment.

---

## 6. Agreed Feature Specifications (v1 Overhaul)

---

### 6.1 LLM Integration & Setup

**What it is:** A configurable LLM backend that powers duration estimation, task breakdown, scheduling suggestions, and the weekly message bank.

**Why it exists:** The app currently uses hardcoded message banks and manual time estimates. LLM integration replaces these with context-aware, dynamic intelligence — while remaining optional so the core app works without it.

**How it works:**

**Settings UI — AI Provider Section:**
- Provider: OPENAI / ANTHROPIC / GOOGLE / OLLAMA / LLAMACPP (5 toggle buttons)
- Cloud providers (OpenAI/Anthropic/Google): API key field + model dropdowns with common models, "Custom..." option for manual entry
- Local providers (Ollama/LlamaCPP): model text inputs + host field (IP:port)
- Two model slots:
  - **QUICK MODEL:** Fast, cheap operations — duration estimates, weekly message bank generation
  - **DEEP MODEL:** Complex operations — task breakdown, scheduling analysis
- TEST CONNECTION button: fires a live API call using current form values (not stale DB values) and returns the actual API error message if it fails
- "?" help button: instructions for each provider

**Provider specifics:**
- **OpenAI:** API key from platform.openai.com. Models: `gpt-4o-mini`, `gpt-4o`, etc.
- **Anthropic:** API key from console.anthropic.com. Models: `claude-haiku-4-5-20251001`, `claude-sonnet-4-6`, `claude-opus-4-8`
- **Google Gemini:** API key from aistudio.google.com. Models: `gemini-2.5-flash`, `gemini-2.5-pro`, etc.
- **Ollama:** Runs on separate desktop machine. Host: `http://192.168.x.x:11434`. Model name must match what Ollama has pulled.
- **LlamaCPP:** Run llama-server with `--port 8080`. Host: `http://192.168.x.x:8080`. Model field defaults to `local` (server picks the loaded model).

**Graceful degradation:**
- If LLM is unavailable (no key, offline, API error), all LLM-dependent features fall back silently:
  - Duration estimation: field left blank, user enters manually
  - Message bank: uses previous week's bank if available, or falls back to pre-written banks
  - Task breakdown: complex toggle disabled with a tooltip explaining why
  - Quick Add: form opens blank, user fills manually
- The core app (add/complete/view tasks, nag system, celebrations) never depends on the LLM

---

### 6.2 Task Duration Field & AI Estimation

**What it is:** A mandatory `duration_minutes` field on every task, displayed as a distinct cell on each task card.

**Why it exists:** The existing app shows time-to-deadline but not work duration. A user could have 2 hours until a deadline but 3 hours of work to do — invisible until it's a crisis. Duration makes the NOW feel of the required work visible, not just the deadline.

**How it works:**

**On the task card (dashboard):**
```
[ ████░░  WRITE CLIENT PROPOSAL   DUE: MON 02 JUN 14:00 ][ 45 MIN ]
```
- Duration is a **separate cell on the far right** of the card
- Existing layout (title, deadline, progress bar) is unchanged on the left
- Duration cell displays the **buffered** time (see 6.3)
- Units: shown in minutes if under 60 (e.g., `45 MIN`), in hours/minutes if over (e.g., `1h 20m`)

**On the Add Task / Edit Task form:**
- Duration field: number input (minutes), labelled "How long will this take?"
- **AI ESTIMATE button** next to the field
  - On press: sends task title + any notes to the QUICK MODEL
  - LLM returns: a brief rationale (2 sentences) + recommended duration in minutes
  - Duration auto-fills the field. User can override.
  - ADHD buffer is applied automatically after the LLM's raw estimate (see 6.3)
  - The field shows the buffered time; the raw estimate is shown briefly as an annotation: "AI estimate: 30 min → buffered to 39 min"
- Duration is **mandatory** — the form cannot be submitted without it

---

### 6.3 ADHD Buffer System

**What it is:** A configurable multiplier applied to all AI-estimated task durations that pads the estimate to account for the consistent ADHD tendency to underestimate time.

**Why it exists:** Research shows ADHD brains underestimate task duration by 30–100% consistently. This is physiological. The buffer corrects for it automatically. Critically, it also gamifies the duration: if the estimate is already generous, the user can ask themselves "can I beat the clock?" — turning a compensation mechanism into a motivational challenge.

**How it works:**
- Default multiplier: **+30%** (raw estimate × 1.3, rounded to nearest 5 minutes)
- Configurable in Settings: "ADHD Buffer %" — user can set any value
- Applied automatically when the AI ESTIMATE button is used
- Not applied to manually entered durations (the user has made a conscious choice)
- Single number shown on the card — the buffered time IS the task's allocated time
- Brief annotation shown in the form immediately after AI estimate: "AI estimate: 30 min → with ADHD buffer: 39 min"
- Framing in the UI: "Your challenge time: 39 MIN" — positions it as a game, not a correction

---

### 6.4 Focus Mode

**What it is:** An active countdown mode that converts a task's duration into a live timer. The user commits to working on a specific task for its allocated time. The whole screen changes to support this.

**Why it exists:** The board currently only shows time-to-deadline. Focus Mode adds the dimension of "I am working on this NOW for X minutes" — closing the loop between planning time and living time.

**How it works:**

**Activation:**
1. User taps/clicks any task card (on dashboard or in the scrollable task list)
2. Popup appears: **"Working on this now?"** with two buttons: **[YES]** and **[NO]**
3. [NO] dismisses — accidental press prevention
4. [YES] → time input screen appears, pre-filled with the task's buffered duration (minutes)
5. User can adjust the time before starting
6. User taps **[START]** → Focus Mode begins

**Focus Mode screen (see 6.5 for full screen layout):**
- Full screen One Task Mode activates immediately (see 6.5)
- Engage sound fires (see 6.18)
- Task card pulses once
- LLM micro-prompt appears for 5 seconds (see 6.7)
- Countdown timer begins

**During Focus Mode:**
- Anti-hyperfocus break reminders fire (see 6.6)
- 2-minute transition warning fires before end (see 6.18)
- User can tap [DONE] to complete the task early → celebration fires
- User can tap [CANCEL] to exit Focus Mode without completing → returns to dashboard, task remains

**When timer hits zero:**
- Escalating nag system activates (same system as deadline nags)
- Gets progressively louder and more aggressive until acknowledged
- User must either mark task DONE or explicitly exit Focus Mode to silence it

---

### 6.5 One Task Mode

**What it is:** A full-screen minimal view that activates automatically when Focus Mode starts. Removes all dashboard clutter and shows only what matters for the current work session.

**Why it exists:** When working, the surrounding task list is a distraction. The ADHD brain will scan the other tasks and lose focus. One Task Mode removes everything but the current task and its timer.

**How it works:**
- Activates automatically when Focus Mode starts — no separate button press
- Deactivates automatically when Focus Mode ends (DONE, CANCEL, or timer expires)
- Cannot be toggled independently — it is the Focus Mode screen

**Screen layout:**
```
┌─────────────────────────────────────────┐
│                                         │
│         WRITE CLIENT PROPOSAL           │
│                                         │
│               32:47                     │
│                                         │
│  [First step: Open the document and     │  ← LLM micro-prompt (fades after 5s)
│   write the first paragraph]            │
│                                         │
│                                         │
│                                         │
│        [  DONE  ]    [ CANCEL ]         │
│                                         │
└─────────────────────────────────────────┘
```
- Task name: large, high-contrast, centre of screen
- Countdown timer: very large, below task name
- LLM micro-prompt: smaller text, fades after 5 seconds
- DONE button: large, prominent — marks task complete and triggers celebration
- CANCEL button: smaller, less prominent — exits Focus Mode without completing

---

### 6.6 Anti-Hyperfocus System

**What it is:** Scheduled break reminders that fire during Focus Mode to prevent the ADHD brain from locking in so deeply that it forgets basic needs (water, toilet, movement) and cannot transition out when needed.

**Why it exists:** Hyperfocus is a double-edged ADHD trait. It enables intense productivity but causes the user to lose track of time, forget physical needs, and struggle to stop when necessary. The system provides external interrupts to counteract this.

**How it works:**

**Break reminder rules:**
| Task Duration | Reminder Schedule |
|---|---|
| Less than 30 minutes | No reminders |
| 30–60 minutes | One reminder at the halfway point |
| More than 60 minutes | Reminder every 30 minutes |

**Reminder content:**
- Visual: a gentle overlay on the Focus Mode screen (does not end the timer)
- Alexa audio: short announcement, e.g., "Time for a quick stretch, drink some water, and take a break if you need one."
- Reminder includes: water, movement, toilet — basic physical needs
- Overlay dismisses after 30 seconds or on user tap

**2-Minute Transition Warning (see also 6.18):**
- A separate, gentler alert fires exactly 2 minutes before the countdown ends
- Gives the ADHD brain time to process the impending transition
- Visual: soft pulsing border on the countdown timer
- Alexa: "[Task name] — two minutes left. Start wrapping up."
- This is distinct from the break reminders — it fires regardless of task duration

---

### 6.7 Task Initiation Trigger

**What it is:** A combined sound + visual + LLM micro-prompt that fires the moment Focus Mode starts, designed to trigger the dopamine response needed to actually begin working.

**Why it exists:** The existing app rewards completion but not initiation. The user identified this as a real problem — they still had to force themselves to start even though completion felt good. The initiation trigger provides a dopamine nudge at the hardest moment: the beginning.

**How it works:**

**On Focus Mode start (simultaneously):**
1. **Engage sound** plays — a short, distinct "let's go" audio clip, different from any completion sound. Signals: work mode is active.
2. **Task card pulses** — a single green flash/pulse on the task card before the screen goes full-screen
3. **LLM micro-prompt** appears on the One Task Mode screen:
   - Generated by the QUICK MODEL
   - Prompt to LLM: "The user is about to start this task: [task title]. Give them ONE specific, concrete first action in 10 words or less. Not motivation. A physical action they can do right now."
   - Example output: "Open the document and write the first sentence."
   - Displayed for 5 seconds then fades
   - If LLM is unavailable, this element is simply absent — no error shown

---

### 6.8 Completion Screen & Weekly Tree

**What it is:** An enhanced completion celebration that adds a persistent gamification mechanic — a weekly growing tree — to the existing fireworks/audio system.

**Why it exists:** The user liked the Forest app's tree mechanic (plant a tree that dies if you leave the app) but wanted something that fits this app's character without making it noisy. The weekly tree gives cumulative visual progress — a "save point" that grows over the week and gives a big reward at the end. Decay mechanics prevent the illusion of progress when tasks are being avoided.

**How it works:**

**Completion sequence:**
1. Smiley dragged onto task (or DONE tapped in Focus Mode)
2. Existing fireworks/confetti/theme animation fires (full screen, as now)
3. Existing randomised Alexa praise message plays
4. After the fireworks: **animated water drop falls onto the weekly tree → tree visibly grows**
5. Return to dashboard (tree visible in background)

**The Weekly Tree:**
- One tree per calendar week (Monday–Sunday)
- Tree lives persistently on the dashboard as a background element — always visible
- Tree starts as a bare trunk/sapling on Monday morning
- **Growth mechanic:** Each completed task causes the tree to grow — new branches, leaves, blossoms appear. Animated water drop precedes each growth event.
- **Decay mechanic:** When tasks are overdue or the day ends with incomplete tasks, small elements fall off the tree (leaves drop, branches shrink). Visible deterioration creates urgency without additional notifications.
- **Weekly reset:** On Monday morning, the tree resets to a new sapling — but the shape, species, and colour palette are randomised each week (different tree types: oak, cherry blossom, pine, etc.). Same gamification, new visual identity.
- **Full week completion reward:** If the user completes all tasks in the week before Sunday midnight, a massive celebration fires — bigger than any single task completion. The fully grown tree has a special flourish (sparkles, birds, etc.) and a large Alexa announcement.

**Technical notes:**
- Tree state (growth level, decay state, current week) stored in DB
- Tree rendering: SVG or Canvas-based animation in the browser
- Tree is a background element on the dashboard — does not obstruct task cards
- Decay calculation runs in the background task checker thread

---

### 6.9 Dashboard Layout Changes

**What it is:** Updates to the main dashboard to accommodate new elements while preserving the existing layout.

**Existing layout (preserve):**
- Top 5 task cards, ordered by deadline
- Each card: progress bar, task title, deadline

**New elements added to dashboard:**

**Task cards (updated):**
```
[ ████░░  WRITE CLIENT PROPOSAL   DUE: MON 02 JUN 14:00 ][ 45 MIN ]
```
- Duration cell added to the far right of each card
- Existing left-side layout unchanged

**Dashboard header area:**
- **"TODAY: Xh [edit]"** chip — shows today's available hours; tap opens quick modal
  - Modal contains: today's hours (editable), tomorrow's hours (editable)
  - No navigation required — modal overlays the dashboard
- **Capacity bar** (conditional): hidden when day is under 80% full; appears in yellow at 80%+, red when over 100%

**Dashboard body:**
- Top 5 tasks (as now)
- Below top 5: scrollable list of ALL remaining tasks (see 6.17 for backlog behaviour)
- Chunky scroll bars throughout — fat-finger friendly, high contrast

**Dashboard footer/controls:**
- Existing: gear icon (settings), nuke button
- New: **WEEK VIEW** button (opens week view screen, see 6.12)
- New: **TONIGHT** button (triggers on-demand evening briefing, see 6.16)
- New: **QUICK ADD** button (opens natural language input, see 6.14)

**Background:**
- Weekly tree rendered as a background element (see 6.8)
- Tree does not obstruct task cards — positioned behind them with appropriate opacity

---

### 6.10 Day Capacity System *(REMOVED)*

> **This system was removed.** Per-weekday hour tracking, the capacity bar, the TODAY chip, and the REBALANCE feature have all been removed. Google Calendar integration provides real scheduling data, making the manual capacity estimation layer redundant. The GCal scheduler uses a simple work window (work_start_hour to work_end_hour) and fills gaps between real calendar appointments.

**What it was:** A system that tracked how many hours of tasks were planned for each day versus how many hours were available, alerting the user when over-committing.

**Why it exists:** ADHD brains are susceptible to optimistic scheduling — adding too many tasks to a day because each individual task feels doable. The capacity system makes the aggregate visible and audible before it becomes a crisis.

**How it works:**

**Daily capacity defaults (Settings):**
- Per-day-of-week settings: Monday through Sunday
- Each day has a default available hours value (e.g., Mon=6h, Sat=3h, Sun=0h)
- These are the baseline assumptions used by the scheduler

**Today/Tomorrow override:**
- "TODAY: Xh [edit]" chip on dashboard header
- Tap → quick modal overlay (no navigation):
  - Today's available hours (editable, pre-filled with weekday default)
  - Tomorrow's available hours (editable, pre-filled with weekday default)
- Changes take immediate effect on the capacity display and scheduler

**Capacity bar (dashboard):**
- Hidden when day is under 80% of available capacity
- Appears in **yellow** at 80–99% full
- Appears in **red** at 100%+ (overloaded)
- Shows: `TODAY [████████░░] 5.5h / 6h` or `TODAY [██████████] OVERLOADED 8h / 6h`
- Updates live as tasks are added, completed, or rescheduled

**Capacity alarm:**
- When adding a task that pushes today's planned time over the available capacity: immediate alarm fires
- Visual: red flash on the capacity bar + warning overlay
- Alexa: "Warning — today is now over capacity. Consider moving a task to another day."
- This fires at the moment of save, not after

---

### 6.11 Auto-Scheduling Engine

> **Implementation note:** This engine (`scheduler.py`) is now Google Calendar-aware. See section 6.20 for the full GCal integration spec. The scheduler places tasks into gaps between real calendar appointments, not hypothetical capacity hours.

**What it is:** A background engine that automatically recalculates the schedule by fitting tasks into gaps between real Google Calendar appointments — and writes scheduled tasks to Google Tasks with times in their titles.

**Why it exists:** Manual rescheduling is a cognitive load that ADHD brains avoid. An invisible engine that handles the logistics reduces the mental overhead of maintaining a realistic schedule.

**How it works:**

**Trigger:**
- Runs automatically in the background whenever:
  - A task is added or edited
  - A task is completed
  - Capacity changes (today/tomorrow override)
  - A task's deadline passes
- After recalculation, if any task needs to move, shows a **confirmation prompt** before moving anything
- Prompt: "Your schedule has changed. I'd like to move [task name] from [day] to [day]. OK?" with [YES] / [NO / SHOW ME OPTIONS]

**Deadline types:**
- **Fixed deadline:** Task has a hard, non-negotiable due date. The scheduler NEVER moves this task. If a fixed-deadline task cannot fit in the day before its deadline, it escalates (Alexa alert, red capacity bar) rather than moving.
- **Flexible deadline:** Task has a target date but can shift. Scheduler can propose moving this task, but always asks for confirmation first.
- **No deadline:** Task has no scheduled date. It is effectively the backlog. The scheduler fills these into days with spare capacity as a reward slot after deadline tasks are complete (see 6.17).

**Cascade order when a day is overfull:**
1. No-deadline tasks move first (no confirmation needed — they have no committed date)
2. Flexible-deadline tasks move next (confirmation required per task or as a batch)
3. Fixed-deadline tasks never move — escalation fires instead

**Clustering:**
- Energy-type clustering (deep work / admin / social) is deferred to v2
- v1 scheduler orders tasks within a day by deadline only

**Week view integration:**
- The REBALANCE button on the week view calls the same scheduling engine for a specific overloaded day
- AI suggests one specific move; user approves or rejects (see 6.12)

---

### 6.12 Week View Screen

**What it is:** A separate screen showing the entire week at a glance as 7 capacity bars, allowing the user to understand their week's workload distribution and manually trigger AI-assisted rebalancing.

**Why it exists:** The main dashboard is day-focused. The week view gives the user a higher-altitude view without the complexity and noise of a full calendar.

**How it works:**

**Access:** WEEK VIEW button on the main dashboard

**Layout:**
```
MON  [████████░░]  5h / 6h   ✓
TUE  [██████████]  6h / 6h   ✓
WED  [████████████] OVERLOADED 8h / 6h  🚨 [REBALANCE]
THU  [████░░░░░░]  3h / 6h   ✓
FRI  [██░░░░░░░░]  1.5h / 6h ✓
SAT  [░░░░░░░░░░]  0h / 3h
SUN  [░░░░░░░░░░]  0h / 0h
```

- Each day shows: day name, capacity bar (coloured green/yellow/red), hours planned vs available
- Tapping a day expands it to show its tasks as a list
- Overloaded days show a **[REBALANCE]** button

**REBALANCE flow:**
1. User taps [REBALANCE] on an overloaded day
2. AI (DEEP MODEL) analyses the day's tasks and the surrounding week's capacity
3. AI proposes ONE specific move: "Move [task name] from [day] to [day]? That gives [day] Xh and [day] Yh."
4. User taps [YES] → task moves, schedule updates
5. User taps [NO] → nothing moves; user can tap [REBALANCE] again for an alternative suggestion
6. Drag-and-drop is NOT implemented in v1 — all rescheduling happens via the REBALANCE flow or editing a task's date

---

### 6.13 Complex Task Breakdown

**What it is:** An AI-powered flow that takes a task the user has flagged as complex and breaks it into a set of sequenced subtasks, each with their own duration, ADHD buffer, and scheduled slot.

**Why it exists:** Complex tasks with many steps are a major ADHD paralysis trigger. "Write the business plan" is too big to start. Breaking it into "Research competitor pricing (30 min)" + "Draft executive summary (45 min)" + "Create financial projections (60 min)" makes each step feel actionable.

**Inspiration:** Goblin Tools' "Magic ToDo" — one-button LLM breakdown. But this implementation goes further by actually scheduling the subtasks into the calendar.

**How it works:**

**Activation:**
- On the Add Task form: a **COMPLEX** toggle
- Toggling it on changes the form flow — after the basic task details are entered, the breakdown flow begins before saving

**Breakdown flow (max 5 questions, dynamic options):**
The LLM (QUICK MODEL) generates up to 5 clarifying questions specific to the task name, each with 2–4 tailored answer options. Questions and options are generated on the fly — not a fixed set. Examples for "Cook Sunday roast for family":
1. "Are you cooking for just yourself, or for others?" [Just me / For others too]
2. "Do you have all the ingredients?" [Yes, ready to go / No, need to shop first]
3. "How familiar are you with this recipe?" [Know it well / Roughly familiar / It's new to me]
4. "Do you need to prep anything the day before?" [Yes / No]
5. "Is there a fixed serving time you're working back from?" [Yes / No — flexible timing]

Each question displays however many buttons its options require (2–4), rendered dynamically. Falls back to generic yes/no questions if the LLM is unavailable. The full question text and chosen answer are passed to the DEEP MODEL for breakdown — richer context than binary yes/no flags.

**Subtask cards:**
After the questions, the DEEP MODEL generates a breakdown displayed as a vertical stack of editable cards. Each card shows title, duration, and suggested date in UK format (e.g. `12 Jun 18:00`). The user can modify the list before saving:

- **EDIT** button on each card — opens an edit popup with the task's title, date (touch picker), time (clock picker), and duration (numpad). Uses the same picker infrastructure as the main Add Task form. Changes are applied immediately to the preview.
- **✕** button — removes the task from the list
- **+ ADD TASK** button at the bottom — opens the same edit popup in new-task mode

**Commit:**
- [COMMIT ALL] button — saves all subtasks to the DB as individual tasks linked to the parent by `parent_task_id`
- Parent task itself is saved as a summary/container task

**Subtask indicators:**
- On the dashboard and task list, subtasks show a small chain icon indicating they belong to a parent
- Tapping the chain icon reveals the parent task and sibling subtasks

**Scheduling logic:**
- The LLM must sequence subtasks correctly (research before writing, etc.)
- The scheduling prompt includes the user's current task list and daily capacity so the LLM can suggest realistic dates
- Sequential subtasks have staggered deadlines automatically
- Subtask durations all have the ADHD buffer applied

**Data sensitivity note:**
- When sending the task list as context to external LLM APIs, task titles and basic metadata are sent
- No personal identifiers beyond what the user has entered
- For users on local Ollama: no external data transfer

---

### 6.14 Quick Add (Touchscreen Form)

**What it is:** A touchscreen-optimised task capture overlay with structured form fields. Tapping QUICK ADD on the dashboard opens it.

**Why it exists:** The original NLP text-area approach ("describe your task, hit PARSE WITH AI") was impractical on a touchscreen without a keyboard. The form-based approach reduces friction to taps — no typing required for most tasks.

**How it works:**

**Access:** [QUICK ADD] button on the main dashboard header

**Form fields (all touchscreen-native):**

1. **TASK NAME** — text input (keyboard opens only for this field)

2. **DEADLINE** — three toggle buttons:
   - **FIXED** (red) — hard, non-moveable deadline
   - **FLEXIBLE** (green) — target date, can shift
   - **NO DATE** (blue) — backlog, no deadline

3. **BY DATE / AT TIME** — hidden when NO DATE selected. Uses:
   - Full-screen year → month → day calendar picker (tap to select)
   - Analog clock picker (drag hands to set time)
   Both pickers are touch-native, no OS keyboard.

4. **DURATION** — six quick-tap buttons: 15 / 30 / 45 / 60 / 90 / 120 min + custom number input. **AI ESTIMATE** button sends the task name to the QUICK MODEL and fills in the estimated + buffered duration.

5. **SAVE TASK** — validates fields and posts directly to `/add`. No AI parsing step.

**The LLM is optional:** if AI ESTIMATE is not tapped, or if the LLM is unavailable, the user enters duration manually. The form always works without AI.

---

### 6.15 LLM Message Bank

**What it is:** A weekly-regenerated bank of 50 messages (nags and praise) generated by the LLM and stored in the DB for use throughout the week.

**Why it exists:** The existing app uses pre-written message banks for Alexa nags and praise. These habituate quickly — the ADHD brain stops registering them after hearing them repeatedly. An LLM-generated bank changes personality each week, preventing habituation while avoiding live API calls on every alert.

**How it works:**

**Generation schedule:**
- Every Monday at 2:00am, a background task fires
- The QUICK MODEL is called with a prompt requesting 50 messages:
  - 25 overdue/nag messages (brutal, snarky British wit tone)
  - 25 completion/praise messages (warm, celebratory tone)
- Messages are stored in a `message_bank` table in the DB
- The previous week's bank is archived (not deleted) — available as fallback

**Message tone (fixed, not a user setting):**
- **Nag messages:** Brutal, snarky, British wit. Direct and slightly cutting. Examples: "Still not done? Remarkable dedication to procrastination." / "This task has been waiting longer than some relationships."
- **Praise messages:** Warm, celebratory, genuine. Examples: "Brilliant! That's one more thing off the board — you're doing great." / "Done! That's what we're talking about. Keep going."
- The contrast between nag and praise tones IS the reward mechanism — do not soften the nags or cool the praise.

**Usage:**
- When an Alexa nag is triggered, the system picks a random unused nag message from the current week's bank
- When a completion praise fires, the system picks a random unused praise message
- Messages are marked as used to avoid repeating within the week
- If all 50 are exhausted before Monday, the system cycles back through them in random order

**Fallback:**
- If Monday 2am generation fails (LLM unavailable), the previous week's bank is used
- If no bank exists at all (first run, LLM never configured), the pre-written hardcoded banks are used as permanent fallback

---

### 6.16 Evening Briefing

**What it is:** An on-demand summary of the day's completions and tomorrow's task preview, triggered by a button on the dashboard.

**Why it exists:** A morning briefing already exists. The evening briefing closes the daily loop — giving the user a sense of accomplishment for the day and a clear picture of what tomorrow looks like. Knowing tomorrow in advance reduces the morning anxiety of "what do I need to do?"

**How it works:**

**Access:** [TONIGHT] button on the main dashboard

**Trigger:** On-demand only — the user taps the button. It does not fire automatically. This is deliberate — the evening is variable, and an automatic trigger at a fixed time may fire at the wrong moment.

**Content (Alexa announcement + dashboard overlay):**
1. Tasks completed today (count + titles)
2. Tasks that rolled over (not completed, moved to future)
3. Tomorrow's top 5 tasks with their allocated durations
4. Tomorrow's capacity status (e.g., "Tomorrow looks full — 5.5h of 6h planned")
5. Optional note if tomorrow is overloaded: "I'd recommend moving [task] to [day] — want me to do that?"

**Tone:**
- Evening briefing tone is calmer than the morning briefing
- Completions celebrated warmly
- Rollovers mentioned matter-of-factly, not critically

---

### 6.17 Backlog (No-Deadline Tasks)

**What it is:** Tasks with no deadline type exist in a permanent backlog state — they are always visible in the scrollable task list but are never urgently scheduled. The auto-scheduler pulls them into days with spare capacity as a "reward slot."

**Why it exists:** Without a backlog, the system cannot capture ideas without forcing a deadline. Forcing a deadline on every task creates artificial urgency and cognitive overhead. The backlog also prevents the user from hiding in low-priority tasks to avoid harder ones — the scheduler only surfaces backlog tasks when deadline tasks have been completed first.

**How it works:**

**Adding to backlog:**
- On the Add Task form, deadline type can be set to "No Deadline"
- No date required
- Task is saved with `deadline_type = 'none'`, no deadline date

**On the dashboard:**
- No-deadline tasks do NOT appear in the top 5 (which is deadline-ordered)
- They appear in the scrollable list below the top 5
- They are visually distinct (e.g., no progress bar — just the task name and duration)
- They are fully interactive from the list (tap to edit, start Focus Mode, or mark done)

**Scheduler behaviour:**
- No-deadline tasks are only scheduled into days when:
  1. The day has spare capacity after all deadline tasks are placed, AND
  2. At least one deadline task was completed that day (reward slot logic)
- This prevents the user accidentally filling a busy day with backlog items to avoid urgent work
- When the scheduler places a no-deadline task into a day, it notifies the user: "You've got some breathing room today. I've added [task] as a bonus task — no pressure."

---

### 6.18 Sound Design

**What it is:** The complete sound event inventory for the app. Sound is a core feature, not decoration — it is the primary ambient alert system for a kiosk app that the user may not be actively watching.

**Sound events:**

| Event | Sound | Via |
|---|---|---|
| Focus Mode starts | Engage sound — short, sharp, distinct "let's go" audio | Local speaker |
| Focus Mode break reminder | Gentle chime or Alexa reminder | Alexa |
| 2 minutes before Focus Mode ends | Soft transition warning sound | Alexa |
| Focus Mode hard stop (time's up) | Escalating nag system begins | Alexa + visual |
| Task completed (celebration) | Randomised applause/praise from LLM bank | Alexa |
| Task overdue (nag) | Escalating nag from LLM bank | Alexa |
| Day capacity exceeded (adding a task) | Immediate capacity alarm | Alexa + visual |
| Weekly tree complete | Massive special celebration | Alexa + visual |
| Morning briefing | Daily task summary | Alexa |
| Evening briefing (on demand) | Task summary and tomorrow preview | Alexa + visual |

**Engage sound:**
- Played via local speaker (not Alexa) for immediate, zero-latency response
- Must be clearly distinct from all other app sounds
- Short (under 2 seconds)
- Energetic, not jarring

**2-minute transition warning:**
- Alexa: "[Task name], two minutes left. Start wrapping up."
- Visual: soft pulsing border on the countdown timer
- Gentle — not alarming. Its purpose is to prepare, not to startle.

**Capacity alarm:**
- Fires immediately when saving a task that pushes the day over capacity
- Alexa: "Warning — today is now over capacity. Consider moving a task."
- Visual: red flash on capacity bar

---

### 6.19 Settings Overhaul

**What it is:** The Settings screen gains several new sections to accommodate the new features.

**New settings sections:**

**AI Provider:**
- Provider: [OpenAI / Anthropic / Local (Ollama)]
- Quick Model: [model name selector for chosen provider]
- Deep Model: [model name selector for chosen provider]
- API Key: [masked input]
- Ollama Host (if Local selected): [IP:port input]
- [TEST CONNECTION] button
- [?] help button

**ADHD Buffer:**
- Buffer %: [number input, default 30]

**Daily Capacity Defaults:**
- Mon / Tue / Wed / Thu / Fri / Sat / Sun: [hours input for each]

**Sounds:**
- Engage sound: [file selector or built-in options]
- Alexa volume: [existing]

**Existing settings (unchanged):**
- Urgency window
- Nuke duration
- Morning briefing time
- Screen size multiplier (Small / Medium / Large)
- Voice Monkey token and device name

---

### 6.20 Google Calendar Integration

**What it is:** Read the user's primary Google Calendar to find busy slots, then schedule app tasks into the gaps between real appointments. Scheduled tasks are written to Google Tasks ("ADHD Tasks" tasklist) with times embedded in the title.

**Why it exists:** The original scheduling engine estimated capacity from manual weekday-hour settings. This was a poor approximation. GCal integration gives the scheduler real data — actual appointments — so scheduled task times are accurate and avoid real conflicts.

**Architecture:**

- `gcal_service.py` — all Google API interactions: OAuth2 token exchange/refresh, calendar reading, Google Tasks CRUD
- `scheduler.py` — pure scheduling algorithm: inserts tasks into gaps between GCal appointments, tightest deadline first

**OAuth flow:**

- Scopes: `calendar.readonly` + `tasks` (read/write)
- Redirect URI: `http://localhost:{port}/gcal_callback` — works in Pi kiosk Chromium
- Tokens stored in settings DB (`gcal_access_token`, `gcal_refresh_token`, `gcal_token_expiry`)
- Auto-refreshes when within 5 minutes of expiry
- `prompt=consent` ensures refresh_token is always returned
- Supports separate Google accounts for Calendar vs GDrive: if `gcal_client_id` / `gcal_client_secret` are set in DB, they take priority over `gdrive_client_id` / `gdrive_client_secret` from config.json

**Calendar reading:**

- Reads primary calendar events for next 21 days
- All-day events ignored (no time slot to conflict with)
- Returns: `{date_str: [(start_naive_local, end_naive_local), ...]}`

**Scheduling algorithm (`scheduler.py`):**

- Sorts tasks by deadline ascending (tightest deadline = highest priority)
- For each task: iterates days from today to deadline
- Per day: work window = `work_start_hour` to `work_end_hour` (configurable, defaults 09:00–17:00)
- Subtracts GCal busy slots + already-allocated slots from this run
- Assigns first gap ≥ task duration
- Backlog / no-deadline tasks skipped (status: `'skipped'`)
- Result statuses: `'scheduled'` | `'unschedulable'` | `'skipped'`

**Google Tasks integration:**

- Creates/updates tasks in "ADHD Tasks" tasklist (created automatically if absent)
- Title format: `"Task Name [Mon 14:00-15:30]"` — time embedded in title for mobile/GCal display
- Updates title + due date if rescheduled (when slot changes on next sync)
- Marks as `status='completed'` when task is done in app — kept for dopamine history
- `gcal_task_id` stored in tasks DB to link app tasks to Google Tasks

**Background sync:**

- `run_gcal_sync()` called from background thread every `gcal_sync_interval_hours` (default 24)
- SYNC NOW button in settings forces immediate sync
- Conflict resolution: on conflict (appointment moved into task slot), scheduler reassigns on next sync automatically
- Unschedulable tasks (no gap before deadline): `scheduled_start` / `scheduled_end` set to NULL

**Settings (GCal section):**

- Status dot: green = connected + active, orange = connected + paused, grey = not connected
- CONNECT / DISCONNECT buttons + last sync time display
- Configurable: sync interval (hours), work day start hour, work day end hour
- Optional: separate `gcal_client_id` / `gcal_client_secret` if Calendar is in a different Google account to GDrive

**Prerequisites for user:**

1. Google Cloud Console: enable Calendar API + Tasks API
2. Create OAuth 2.0 credentials (Web application type)
3. Add `http://localhost:{port}/gcal_callback` as Authorised Redirect URI
4. Connect in Settings → Google Calendar Sync → CONNECT GOOGLE CALENDAR

---

## 7. Data Model

Changes required to the existing SQLite database.

### 7.1 Tasks Table (updated)

```sql
ALTER TABLE tasks ADD COLUMN duration_minutes INTEGER;
ALTER TABLE tasks ADD COLUMN deadline_type TEXT DEFAULT 'fixed'; 
  -- values: 'fixed', 'flexible', 'none'
ALTER TABLE tasks ADD COLUMN parent_task_id INTEGER REFERENCES tasks(id);
ALTER TABLE tasks ADD COLUMN buffer_applied REAL DEFAULT 1.3;
ALTER TABLE tasks ADD COLUMN is_subtask INTEGER DEFAULT 0;
ALTER TABLE tasks ADD COLUMN energy_type TEXT;
  -- reserved for v2: 'deep', 'admin', 'social'
ALTER TABLE tasks ADD COLUMN gcal_task_id TEXT;       -- Google Tasks ID (null if not synced)
ALTER TABLE tasks ADD COLUMN scheduled_start TEXT;    -- ISO datetime from GCal scheduler
ALTER TABLE tasks ADD COLUMN scheduled_end TEXT;      -- ISO datetime from GCal scheduler
```

### 7.2 Daily Capacity Tables *(REMOVED)*

> These tables (`daily_capacity`, `capacity_overrides`) have been removed. Capacity tracking is superseded by real Google Calendar data.

### 7.3 Settings Table Keys (additions)

```
llm_provider         TEXT    -- 'openai', 'anthropic', 'google', 'ollama', 'llamacpp'
llm_quick_model      TEXT    -- e.g. 'gpt-4o-mini', 'gemini-2.5-flash'
llm_deep_model       TEXT    -- e.g. 'gpt-4o', 'claude-opus-4-8'
llm_ollama_host      TEXT    -- e.g. 'http://192.168.1.50:11434'
llm_api_key          TEXT    -- API key (cloud providers)
adhd_buffer_pct      REAL    -- default 30.0

gcal_enabled         TEXT    -- '0' or '1'
gcal_access_token    TEXT    -- OAuth2 access token (managed by gcal_service)
gcal_refresh_token   TEXT    -- OAuth2 refresh token (managed by gcal_service)
gcal_token_expiry    TEXT    -- ISO datetime of access token expiry
gcal_tasklist_id     TEXT    -- "ADHD Tasks" tasklist ID (cached)
gcal_sync_interval_hours TEXT -- default '24'
gcal_work_start_hour TEXT    -- default '9' (9 = 09:00)
gcal_work_end_hour   TEXT    -- default '17' (17 = 17:00)
gcal_last_sync       TEXT    -- datetime of last successful sync
gcal_client_id       TEXT    -- optional: Calendar-specific OAuth client ID
gcal_client_secret   TEXT    -- optional: Calendar-specific OAuth client secret
```

### 7.4 Message Bank Table (new)

```sql
CREATE TABLE message_bank (
  id INTEGER PRIMARY KEY,
  week_start DATE NOT NULL,         -- Monday date of the week
  message_type TEXT NOT NULL,       -- 'nag' or 'praise'
  message_text TEXT NOT NULL,
  used INTEGER DEFAULT 0,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 7.5 Weekly Tree Table (new)

```sql
CREATE TABLE weekly_tree (
  id INTEGER PRIMARY KEY,
  week_start DATE NOT NULL UNIQUE,
  tree_variant TEXT NOT NULL,       -- randomised tree type/style key
  growth_level REAL DEFAULT 0.0,    -- 0.0 = sapling, 1.0 = fully grown
  is_complete INTEGER DEFAULT 0,    -- 1 = full week completion achieved
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 7.6 Focus Sessions Table (new)

```sql
CREATE TABLE focus_sessions (
  id INTEGER PRIMARY KEY,
  task_id INTEGER REFERENCES tasks(id),
  started_at DATETIME NOT NULL,
  planned_duration_minutes INTEGER NOT NULL,
  ended_at DATETIME,
  end_reason TEXT,  -- 'completed', 'cancelled', 'expired'
  break_reminders_fired INTEGER DEFAULT 0
);
```

---

## 8. Architecture Overview

### 8.1 Backend (Python/Flask)

**Modules implemented:**

- `llm_service.py` — LLM API wrapper. 5 providers: OpenAI, Anthropic, Google Gemini, Ollama, LlamaCPP. Handles API key management, live form value overrides for TEST CONNECTION, real error message extraction, graceful fallback. `call_llm(prompt, model_type, overrides)` is the main entry point.
- `scheduler.py` — Pure scheduling algorithm. `schedule_tasks(tasks, busy_slots_by_date, work_start_float, work_end_float)` — tightest-deadline-first, fills gaps in the work window between GCal busy slots. No dependency on capacity settings.
- `gcal_service.py` — Google Calendar + Tasks API wrapper. OAuth2 flow (auth URL, code exchange, token refresh), `fetch_busy_slots()`, `get_or_create_tasklist()`, `create_task()`, `update_task()`, `complete_task()`, `delete_task()`. Separate credential support for Calendar vs GDrive accounts.

**Modules not yet separated (still in app.py):**
- Focus Mode state management (focus_sessions table, break reminder logic)
- Weekly tree state management (weekly_tree table, grow/decay logic)
- Message bank management (message_bank table, weekly generation)

**Existing background thread (`background_task_checker`):**
- Extended to include: tree decay calculation, Monday 2am message bank generation, Focus Mode break reminder scheduling, capacity monitoring

### 8.2 Frontend (HTML/JS/CSS)

**New screens/components:**
- `focus_mode.html` — One Task Mode full-screen overlay
- `week_view.html` — Week view screen with 7 day bars
- `tree_component.js` — Weekly tree SVG/Canvas animation
- `quick_add.html` — Natural language input overlay

**Existing templates updated:**
- `index.html` — Dashboard layout changes (capacity bar, QUICK ADD, WEEK VIEW, TONIGHT buttons, tree background, duration cells on cards)
- `add.html` — Duration field, AI ESTIMATE button, COMPLEX toggle, QUICK ADD flow
- `edit_task.html` — Duration field, deadline type selector
- `settings.html` — New AI Provider and Capacity sections

### 8.3 Config

- `config.json` stores: Voice Monkey token, LLM API keys, Ollama host
- `config.json` is gitignored — never committed
- `config.json.example` updated to include new LLM fields with placeholder values and comments

---

## 9. UI/UX Principles

These apply to every screen and component in the overhaul.

1. **Chunky scroll bars everywhere** — High contrast, wide, easy to grab with fat fingers
2. **Minimum tap target: 48px** — No small buttons anywhere
3. **Internal keyboard for all text input** — Never trigger the OS keyboard (it disrupts kiosk layout)
4. **No more than 3 taps to complete any core action** — Add task, complete task, start Focus Mode
5. **Single question per screen/popup** — Never ask two things at once
6. **Options not typing** — Where possible, present choices rather than require text input
7. **High contrast always** — Dark background, bright text, clear distinction between states
8. **Visible from 3 metres** — The most important dashboard info (overdue state, top task, capacity) must be legible from across a room
9. **No silent failures** — If something goes wrong (LLM unavailable, API error), the UI degrades gracefully but the user never sees an unhandled error
10. **Randomise everything** — Celebration themes, tree structures, messages — predictability is the enemy of engagement for ADHD brains

---

## 10. Competitive Landscape

Understanding what the competition does informs what we must NOT become.

| App | Standout Feature | What It Lacks |
|---|---|---|
| Motion | True AI auto-scheduler | No kiosk, no audio, no ADHD visual urgency |
| Tiimo | Visual timeline, neurodivergent-designed | No voice alerts, no LLM, passive not aggressive |
| Amazing Marvin | Deep customisation, gamification | Requires constant configuration, no kiosk |
| Goblin Tools | "Magic ToDo" LLM task breakdown | Standalone, not integrated scheduler |
| Forest | Tree gamification | Not a task manager |
| Reclaim.ai | Calendar-aware AI scheduling | No kiosk, no ADHD design, very corporate |
| Structured | Beautiful visual timeline | No voice, no LLM, no aggression |
| Focusmate | Virtual body doubling | Not a task manager |

**Our unique position:** The ONLY product combining kiosk/ambient mode + Alexa escalating nag system + ADHD-specific visual urgency + LLM-wired scheduler + celebration finale + neuroscience-backed design philosophy. Each of these exists somewhere in the market. No competitor has all of them.

---

## 11. V2 Ideas (Deferred)

These ideas were discussed and agreed as out of scope for v1. They should be revisited after v1 is stable.

### 11.1 Energy Type Clustering
Tag tasks as Deep Work / Admin / Social. Colour-code cards (blue/grey/green). Scheduler clusters same-type tasks together — deep work in the morning, admin in the afternoon. Scientifically grounded in ADHD energy variability patterns.

### 11.2 Weekly Planning Ritual
A Sunday evening LLM-facilitated planning session. User reviews the week ahead, confirms available hours, checks that everything fits. Alexa guides the session conversationally. The anchor that makes the whole system self-maintaining long-term.

### 11.3 Emotional State Check-In
A 3-second check at the start of the day (or on app open): "Energy today? [LOW / MEDIUM / HIGH]". If LOW, the scheduler automatically lightens the day's plan and surfaces only the must-do items. Addresses ADHD energy variability that no competitor currently handles.

### 11.4 Body Doubling (LLM as Companion)
When Focus Mode starts: a short LLM-generated message: "I'm working alongside you. Let's get this done." When the timer ends: "How did that go? What's next?" The psychological effect of "someone else knows I'm working" is a well-documented ADHD focus aid.

### 11.5 Shame Spiral / Reset Day Button
A compassionate overflow mechanism for bad days. A "RESET DAY" button that non-judgementally rolls all of today's incomplete tasks forward to tomorrow. No "TASK EXPIRED" in harsh red — just a clean slate. For the days when the system itself becomes an emotional burden.

### 11.6 Rotating Daily Background
Subtly rotate the dashboard background colour scheme daily within a defined dark palette. Fights habituation without adding noise. The ADHD brain's pattern blindness means even ambient visual variety helps maintain engagement with the screen.

### 11.7 Micro-Wins Jackpot
Occasionally, at random, trigger an unexpected over-the-top celebration when completing a small task. Ultra rare — like a slot machine jackpot. The unpredictability is itself dopaminergic. The rarity makes it feel genuinely surprising every time.

### 11.8 Mobile Interface *(NEXT PLANNED PHASE)*

> **Actively planned** — the next development phase after kiosk v2 is stable.

A mobile-friendly simplified interface accessible over Tailscale from anywhere. The kiosk app runs on the Pi; the mobile interface connects to it remotely. Google Calendar integration means the schedule is already synced — the mobile view just needs to show it and allow quick task management.

**Planned scope:**
- Responsive/touch-friendly layout optimised for phone screens
- View today's tasks with scheduled times (from GCal sync)
- Quick complete, quick add (minimal form)
- Focus Mode timer on phone
- Push notification equivalents of deadline nags (via Tailscale-accessible API)

The existing `/mobile` route is a stripped-down add/complete interface — this would be a significant upgrade to a full mobile experience.

### 11.9 Natural Language Voice Input
"Hey, add a task: call the accountant on Friday, about 30 minutes." Voice-to-text piped through the Quick Add LLM parser. Removes the keyboard entirely for task capture moments.

### 11.10 Expanded Celebration Themes
Currently 5 visual celebration themes. Target is 15+. More themes = longer before habituation sets in. Possible themes: space explosion, pixel art level-up, retro arcade, nature bloom, dramatic orchestral, among others.

### 11.11 Multi-User Support
The app is currently single-user. A multi-user mode would allow a household (e.g., two ADHD adults) to share the kiosk with separate task lists and capacity settings, while sharing the same ambient screen.

---

*End of Blueprint. Last updated 2026-06-07 to reflect Sessions 001–008. For session-by-session implementation details, see PROGRESS.md. Any spec changes should be reflected here before coding begins.*
