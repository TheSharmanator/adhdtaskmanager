import calendar
import re
import signal
import sqlite3
import subprocess
import requests
import random
import os
import threading
from flask import Flask, render_template, request, redirect, jsonify, send_from_directory
from datetime import datetime, timedelta, date

import llm_service

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

# --- CONFIGURATION ---
USER_NAME = 'User'  # fallback only; real name comes from DB settings

VOICES = [
    "Nicole", "Russell", "Amy", "Emma", "Brian",
    "Raveena", "Aditi", "Ivy", "Joanna", "Kendra",
    "Kimberley", "Salli", "Joey", "Justin", "Matthew",
    "Geraint", "Celine", "Lea", "Mathieu"
]

MORNING_QUOTES = [
    "The sun is up, and so are the stakes.",
    "Fortune favours the bold, so stop hesitating.",
    "Every day is a fresh roll of the dice.",
    "Action is the foundational key to all success.",
    "The only way to predict the future is to build it.",
    "Efficiency is doing things right; effectiveness is doing the right things.",
    "Get after it.",
    "Small gains every day lead to massive results.",
    "The best revenge is massive success.",
    "Discipline is the bridge between goals and accomplishment.",
    "Amateurs sit and wait for inspiration, the rest of us just get up and go to work.",
    "Focus on the signal, ignore the noise.",
    "The obstacle is the way.",
    "Consistency beats intensity every single time.",
    "Wake up with determination, go to bed with satisfaction.",
    "Control your morning, control your day.",
    "Don't count the days, make the days count.",
    "Simplicity is the ultimate sophistication.",
    "Energy flows where attention goes.",
    "You don't have to be great to start, but you have to start to be great.",
    "Great things never come from comfort zones.",
    "Be the hammer, not the anvil.",
    "Own your time or someone else will.",
    "The secret of getting ahead is getting started.",
    "Hard work beats talent when talent doesn't work hard.",
    "Pressure creates diamonds.",
    "Today is a good day for a breakthrough.",
    "Don't wait for opportunity. Create it.",
    "It's a beautiful day to disrupt the status quo.",
    "Maximum effort, minimum fluff.",
    "Make it happen.",
    "You are the architect of your own reality.",
    "Start where you are. Use what you have. Do what you can.",
    "The day is yours for the taking.",
]

PRAISE_MESSAGES = [
    "I've never seen anyone handle a workload with that level of clinical precision, {name}, you're in a league of your own.",
    "That was a world-class bit of execution, {name}, you've genuinely set a benchmark that nobody else is going to touch.",
    "You've got a rare talent for cutting through the noise and delivering pure quality, {name}, it's impressive to watch.",
    "The level of detail you've managed to maintain under that kind of pressure is nothing short of elite, {name}.",
    "You've absolutely played a blinder, {name}, that's the kind of high-spec finish that separates the pros from the amateurs.",
    "I knew you were capable of great work, {name}, but you've managed to exceed even my highest expectations on this one.",
    "That was a masterclass in efficiency and grit, {name}, you've made a complex task look like a walk in the park.",
    "Your ability to stay grounded and deliver such a polished result is a testament to your focus, {name}.",
    "You've navigated that like a total expert, {name}, I don't think there's a single person who could have done it better.",
    "There's a real craft to the way you work, {name}, and the results speak volumes about your standards.",
    "You've delivered a result that is both functional and flawless, {name}, you should be incredibly proud of that graft.",
    "The sheer momentum you maintained to get this finished to such a high standard is remarkable, {name}.",
    "You've got a habit of making the impossible look standard, {name}, and this was no exception.",
    "That was a legendary performance, {name}, you've handled every variable with total composure and skill.",
    "You've turned in a piece of work that is head and shoulders above the rest, {name}, absolutely top-tier stuff.",
    "It's rare to see someone operate with that level of clarity and purpose, {name}, you've nailed it.",
    "You've taken the brief and elevated it into something truly exceptional, {name}, credit to your vision.",
    "The way you've tightened up every loose end is a display of pure professional excellence, {name}.",
    "You've got an engine on you, {name}, I'm genuinely floored by how much quality you've packed into this.",
    "That was a surgical strike of a job, {name}, you went in, did the work, and left everyone else standing.",
    "That's a gold-plated result if ever I saw one, {name}, you've hit the bullseye and then some.",
    "Your consistency is your greatest weapon, {name}, and you've just fired another winning shot with this.",
    "That was a deeply impressive display of competence, {name}, you've made a massive impact today.",
    "You've treated this task with the respect and focus it deserved, {name}, and the outcome is flawless.",
    "There's no fluff or filler in what you've produced, {name}, it's just pure, unadulterated quality.",
    "That's the kind of work that builds a reputation of iron, {name}, you've absolutely crushed it.",
    "The clarity of your execution is honestly refreshing, {name}, you've simplified the complex and won.",
    "You've put a real stamp of authority on this project, {name}, nobody can doubt your expertise now.",
    "That was a marathon effort with a sprint finish, {name}, and you didn't miss a single beat.",
    "You've produced something that is as robust as it is refined, {name}, a truly professional job.",
    "You've outclassed the requirements and delivered something truly special, {name}.",
    "That was a high-performance delivery from start to finish, {name}, you're firing on all cylinders.",
    "You've got a way of making every move count, {name}, and this result is the ultimate proof.",
    "That's a textbook example of how to handle a high-stakes task, {name}, you were flawless.",
    "You've managed to turn hard graft into a work of art, {name}, you're a credit to your craft.",
    "You've delivered a powerhouse of a result, {name}, it's solid, it's sharp, and it's done.",
    "That was an incredibly slick operation, {name}, you've handled it with total finesse.",
    "Your standards are sky-high, {name}, and you've just cleared the bar with plenty of room to spare.",
    "That was a brilliantly executed piece of work that shows exactly why you're the best at what you do, {name}.",
    "You've finished this with such authority and style, {name}, it's an absolute win for the books.",
]

LATE_PRAISE_MESSAGES = [
    "Better late than never, {name}, though in this specific case, \"never\" was actually a viable contender.",
    "If time is a flat circle, {name}, then technically you've smashed it. If it's linear, we have a problem.",
    "Incredible stuff, {name}. I'll notify the history museums that the missing era has finally concluded.",
    "I'd applaud, {name}, but the kinetic energy required feels a bit redundant at this point in the century.",
    "Outstanding, {name}. The deadline passed so long ago it's actually achieved vintage status.",
    "Look at you go, {name}. Proof that if you wait long enough, the urgency solves itself anyway.",
    "Brilliant. I'll go tell the client to uncancel the funeral, shall I, {name}?",
    "A masterclass in suspense, {name}. I genuinely didn't think I'd live to see the final act.",
    "Spot on, {name}. Just a few days short of a calendar miracle.",
    "If we were measuring this in dog years, {name}, you'd be a digital archaeologist right now.",
    "It's a masterpiece, {name}. Much like the Sagrada Família, we weren't sure it would happen in our lifetime.",
    "Splendid work, {name}. The panic we felt last Tuesday has officially ripened into mild amusement.",
    "Fast? No. Thorough? Also debatable. But it is here, {name}, and that's what we'll tell the police.",
    "Quick, {name}, let's file this away before the sun burns out and renders the whole thing moot.",
    "You've really captured the essence of \"scenic route\" with this one, {name}.",
    "Truly, {name}, your commitment to ignoring the space-time continuum is nothing short of heroic.",
    "I didn't realise we were operating on GMT — Grievously Miscalculated Time, {name}.",
    "Absolute lightning speed, {name}. Assuming we are tracking the movement of tectonic plates.",
    "Well, {name}, the project has evolved, the client has retired, but your contribution is safely logged.",
    "Huzzah, {name}. The ghost ship has finally drifted into harbor.",
]

NAG_30 = [
    "Sunshine. Tick tock.",
    "The sand's running out of the glass.",
    "Don't make me tap the sign.",
    "This isn't a drill.",
    "Better get a move on.",
    "The clock is winning right now.",
    "Speed it up, or we're stuffed.",
    "Efficiency is your only friend now.",
    "No more faffing about.",
    "The reaper is at the door.",
    "Panic is optional; finishing isn't.",
    "Put your back into it.",
    "Eyes on the prize.",
    "You're cutting it fine, aren't you?",
    "This is the home stretch.",
    "Less thinking, more doing.",
    "Don't drop the ball now.",
    "The guillotine is being sharpened.",
    "Your time's almost up.",
    "Last chance to look like a pro.",
    "Shake a leg.",
    "The window is closing.",
    "Make every second count.",
    "Clock's ticking.",
    "It's now or never.",
    "Focus up, work harder.",
    "This isn't a social club.",
    "Final warning.",
    "Time to deliver or disappear.",
    "The cliff edge is right there.",
    "Hustle, before it's too late.",
    "Stop watching the clock and start beating it.",
    "You're on borrowed time.",
    "Get it done, no excuses.",
    "The bells are about to toll.",
    "It's crunch time.",
    "Pull your finger out.",
    "Just half an hour left.",
    "Wrap it up.",
]

NAG_15 = [
    "Last chance. Move it.",
    "The clock has already beaten you half to death.",
    "Fifteen minutes or you're finished.",
    "Stop breathing and start doing.",
    "This is the point of no return.",
    "The axe is mid-swing.",
    "Total focus. Right now.",
    "You're out of runway.",
    "Move like your life depends on it.",
    "Zero room for error left.",
    "The walls are closing in.",
    "Pick up the pace or pack it in.",
    "The timer is screaming.",
    "Every second you waste is a nail in the coffin.",
    "This is a crisis, act like it.",
    "Cut the rubbish and deliver.",
    "Shift it. Now.",
    "The fuse is down to the last inch.",
    "The grace period is dead.",
    "Finish it or face the music.",
    "Don't you dare stop moving.",
    "The pressure is on. Deal with it.",
    "Final sprint. No more talking.",
    "There is no more 'later'.",
    "Fifteen minutes. Make them count.",
    "Shut up and finish.",
    "The bells are ringing.",
    "This is your final, final warning.",
    "Put the hammer down.",
    "Done. Now.",
]

NAG_DEADLINE = [
    "The clock has stopped. You've run out of road.",
    "The silence is deafening.",
    "You had the warnings and you blew it.",
    "There's the line, and you're on the wrong side of it.",
    "I expected a result, not a post-mortem.",
    "You've let the clock win.",
    "The window isn't just closed; it's locked.",
    "All that talk for nothing.",
    "The opportunity has evaporated.",
    "I'm looking at a void where a finished task should be.",
    "You've managed to snatch defeat from the jaws of victory.",
    "The sand is gone. The glass is empty.",
    "Is this it? Is this the best we can expect?",
    "The deadline didn't move; you just stayed still.",
    "Hope you enjoyed the faffing, because the price is high.",
    "A total collapse of execution.",
    "The bells have tolled and you're still at the starting block.",
    "Zero. Zilch. Nothing to show for it.",
    "The reaper isn't at the door anymore; he's moved in.",
    "You had every chance to deliver.",
    "The guillotine has dropped.",
    "Utterly underwhelming.",
    "It's over. You missed the boat.",
    "The runway ended and you didn't even take off.",
    "I'm not angry, just profoundly unimpressed.",
    "The time for excuses expired sixty seconds ago.",
    "You've failed the most basic requirement: finishing.",
    "The lights are off and the doors are barred.",
    "A masterclass in how to fail.",
    "The countdown reached zero and you blinked.",
]

NAG_EXPIRED = [
    "The ship hasn't just sailed; it's over the horizon and sinking.",
    "We're well into the autopsy phase now.",
    "The clock is mocking us.",
    "This isn't a delay; it's a monument to inertia.",
    "We've moved past 'late' and straight into 'pointless'.",
    "The urgency died hours ago; now it's just embarrassing.",
    "Staring at a carcass where a project should be.",
    "The deadline is a distant memory.",
    "You're not just behind the curve; you've fallen off the map.",
    "Collecting dust on a ghost task.",
    "Post-deadline faffing is the worst kind of faffing.",
    "It's yesterday's news and you haven't even printed it yet.",
    "This is a masterclass in 'too little, too late'.",
    "Are we waiting for a miracle or just a pulse?",
    "The silence on this is getting loud.",
    "You're dragging an anchor through a desert.",
    "The lights went out a long time ago.",
    "The expiry date wasn't a suggestion.",
    "Beyond late. Beyond excuses.",
    "The reaper has grown old waiting for this.",
    "Total system failure.",
    "The countdown hit zero and then kept going into the negatives.",
    "It's a ghost ship. No one's at the helm.",
    "You've turned a task into a legend of procrastination.",
    "The world moved on; you didn't.",
    "The bells stopped tolling because they gave up.",
    "A void where effort used to live.",
    "The deadline is ancient history.",
    "Is there anyone actually in there?",
    "You've missed the boat, the train, and the point.",
]

CHIMES = [
    "soundbank://soundlibrary/alarms/air_horns/air_horn_01",
    "soundbank://soundlibrary/alarms/beeps_and_bloops/boing_01",
    "soundbank://soundlibrary/alarms/buzzers/buzzers_01",
    "soundbank://soundlibrary/alarms/buzzers/buzzers_04",
    "soundbank://soundlibrary/alarms/chimes_and_bells/chimes_bells_04",
    "soundbank://soundlibrary/home/amzn_sfx_doorbell_01",
    "soundbank://soundlibrary/home/amzn_sfx_doorbell_chime_02",
    "soundbank://soundlibrary/scifi/amzn_sfx_scifi_timer_beep_01",
    "soundbank://soundlibrary/scifi/amzn_sfx_scifi_alarm_01",
    "soundbank://soundlibrary/alarms/beeps_and_bloops/buzz_03",
    "soundbank://soundlibrary/musical/amzn_sfx_test_tone_01",
]

FOCUS_NUDGES = [
    "Stay on task. Nothing else exists right now.",
    "No side quests. Finish what you started.",
    "Ignore the shiny thing. It will still be there later.",
    "One thing. This thing. Right now.",
    "Put the phone down.",
    "You were doing something. Keep going.",
    "Don't open a new tab.",
    "Momentum is your friend. Don't break it.",
    "Not now. Later. Focus.",
    "Rabbit holes are for rabbits.",
    "New idea? Write it down and come back to this.",
    "Eyes forward. You're doing it.",
    "The other thing can wait. This one can't.",
    "You started this. Finish it.",
    "Time blindness check: are you still on task?",
    "Don't fix something that isn't your task.",
    "Hyper-focus on the right thing. This thing.",
    "Distraction is the enemy. You are stronger.",
    "One tab. One task. One goal.",
    "Still there? Good. Keep going.",
    "The urge to switch is not an emergency. Ignore it.",
    "No quick checks. No just-one-minutes. Stay.",
    "You are in the zone. Stay in the zone.",
    "Interruptions compound. Block them all.",
    "Your future self will thank you for finishing this.",
    "Brain wandering? Bring it back. Now.",
    "This is the task. Not the other one. This one.",
    "Steady. You're closer than you think.",
]

NO_DEADLINE_SENTINEL = '2099-12-31T00:00'


def _is_dnd_time(now_time, dnd_start, dnd_end):
    if dnd_start > dnd_end:
        return now_time >= dnd_start or now_time <= dnd_end
    return dnd_start <= now_time <= dnd_end


def _enrich_focus_session(session):
    if session:
        started = datetime.strptime(session['started_at'], '%Y-%m-%d %H:%M:%S')
        session['elapsed_seconds'] = int((datetime.now() - started).total_seconds())
        session['session_id'] = session['id']
    return session


def get_db():
    conn = sqlite3.connect('tasks.db', timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    conn = get_db()
    c = conn.cursor()

    # --- Core tables ---
    c.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            deadline TEXT NOT NULL,
            status TEXT DEFAULT 'active',
            last_alert_type TEXT DEFAULT 'none',
            last_nag_time TEXT,
            percent INTEGER DEFAULT 0,
            phase TEXT,
            duration_minutes INTEGER DEFAULT 30,
            deadline_type TEXT DEFAULT 'flexible',
            parent_task_id INTEGER,
            buffer_applied REAL DEFAULT 1.3
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS recurring_templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            start_time TEXT NOT NULL,
            interval TEXT NOT NULL,
            last_generated TEXT,
            end_date TEXT,
            duration_minutes INTEGER DEFAULT 30
        )
    """)
    # Migration: add end_date column if missing (existing DBs)
    try:
        c.execute("ALTER TABLE recurring_templates ADD COLUMN end_date TEXT")
    except:
        pass  # column already exists
    try:
        c.execute("ALTER TABLE recurring_templates ADD COLUMN duration_minutes INTEGER DEFAULT 30")
    except:
        pass  # column already exists
    c.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """)

    # --- New v2 tables ---
    c.execute("""
        CREATE TABLE IF NOT EXISTS focus_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER,
            task_title TEXT,
            started_at TEXT NOT NULL,
            planned_minutes INTEGER NOT NULL,
            ended_at TEXT,
            end_reason TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS message_bank (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            week_start DATE NOT NULL,
            message_type TEXT NOT NULL,
            message_text TEXT NOT NULL,
            used INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Migrate existing tasks table to add new columns if needed
    for col, definition in [
        ('duration_minutes', 'INTEGER DEFAULT 30'),
        ('deadline_type', "TEXT DEFAULT 'flexible'"),
        ('parent_task_id', 'INTEGER'),
        ('buffer_applied', 'REAL DEFAULT 1.3'),
        ('gcal_task_id', 'TEXT'),
        ('scheduled_start', 'TEXT'),
        ('scheduled_end', 'TEXT'),
        ('pin_to_date', 'INTEGER DEFAULT 0'),
        ('unschedulable', 'INTEGER DEFAULT 0'),
    ]:
        try:
            c.execute(f'ALTER TABLE tasks ADD COLUMN {col} {definition}')
        except Exception:
            pass  # Column already exists

    # Default settings
    defaults = [
        ('briefing_time', '08:00'),
        ('dnd_start', '22:00'),
        ('dnd_end', '07:00'),
        ('nag_interval', '15'),
        ('port', '5001'),
        ('bar_start_hours', '24'),
        ('adhd_buffer_pct', '30'),
        ('briefing_days', 'Mon,Tue,Wed,Thu,Fri'),
        ('evening_briefing_time', '21:00'),
        ('gcal_enabled', '0'),
        ('gcal_sync_interval_hours', '24'),
        ('vm_enabled', '0'),
        ('vm_token', ''),
        ('vm_device_alerts', ''),
        ('vm_device_briefings', ''),
        ('vm_device_evening', ''),
        ('vm_device_focus', ''),
        ('vm_language', 'en-GB'),
        ('backup_enabled', '0'),
        ('gdrive_client_id', ''),
        ('gdrive_client_secret', ''),
        ('setup_complete', '0'),
    ]
    for key, val in defaults:
        c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (key, val))

    conn.commit()
    conn.close()


# --- HELPERS ---

def trigger_voice_monkey(text, device=None, chime=None):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT key, value FROM settings WHERE key IN ("
              "'vm_enabled','vm_token','vm_device_alerts','vm_language',"
              "'dnd_start','dnd_end','silence_mode')")
    sets = {row[0]: row[1] for row in c.fetchall()}
    conn.close()

    vm_enabled = sets.get('vm_enabled', '0') == '1'
    vm_token   = sets.get('vm_token', '')
    if not vm_enabled or not vm_token:
        print(f"[VM] skipped — vm_enabled={vm_enabled} token={'set' if vm_token else 'missing'}")
        return

    if sets.get('silence_mode') == 'on':
        print("[VM] skipped — silence mode is ON")
        return

    dnd_start = sets.get('dnd_start', '22:00')
    dnd_end   = sets.get('dnd_end', '07:00')
    now_hm    = datetime.now().strftime('%H:%M')
    if _is_dnd_time(now_hm, dnd_start, dnd_end):
        print(f"[VM] skipped — DND active ({now_hm}, window {dnd_start}–{dnd_end})")
        return

    target_device = device or sets.get('vm_device_alerts', '')
    if not target_device:
        print("[VM] skipped — no target device configured")
        return

    url = "https://api-v2.voicemonkey.io/announcement"
    params = {
        "token":    vm_token,
        "device":   target_device,
        "text":     text,
        "voice":    random.choice(VOICES),
        "language": sets.get('vm_language', 'en-GB'),
    }
    if chime:
        params["chime"] = chime
    try:
        r = requests.get(url, params=params, timeout=5)
        print(f"[VM] sent to '{target_device}': {text[:60]!r} — HTTP {r.status_code}")
    except Exception as e:
        print(f"[VM] request failed: {e}")


def get_setting(key, default=None):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT value FROM settings WHERE key=?", (key,))
    res = c.fetchone()
    conn.close()
    return res[0] if res else default


def set_setting(key, value):
    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, str(value) if value is not None else ''))
    conn.commit()
    conn.close()


def get_user_name():
    return get_setting('user_name', None) or USER_NAME


def get_buffer_pct():
    try:
        return float(get_setting('adhd_buffer_pct', '30'))
    except Exception:
        return 30.0


def format_duration(minutes):
    if not minutes:
        return '—'
    try:
        m = int(minutes)
        if m < 60:
            return f'{m} MIN'
        h = m // 60
        rem = m % 60
        return f'{h}h {rem}m' if rem else f'{h}h'
    except Exception:
        return '—'


def get_message_from_bank(msg_type):
    """Get a random unused message from the current week's bank. Falls back to built-in lists."""
    today = date.today()
    monday = today - timedelta(days=today.weekday())
    week_str = monday.isoformat()

    conn = get_db()
    c = conn.cursor()
    c.execute(
        "SELECT id, message_text FROM message_bank WHERE week_start=? AND message_type=? AND used=0 ORDER BY RANDOM() LIMIT 1",
        (week_str, msg_type)
    )
    row = c.fetchone()
    if row:
        c.execute("UPDATE message_bank SET used=1 WHERE id=?", (row[0],))
        conn.commit()
        conn.close()
        return row[1]

    conn.close()
    # Fallback to built-in
    if msg_type == 'nag':
        return random.choice(NAG_EXPIRED)
    if msg_type == 'focus_nudge':
        return random.choice(FOCUS_NUDGES)
    return random.choice(PRAISE_MESSAGES).format(name=get_user_name())


def get_active_focus_session():
    conn = get_db()
    c = conn.cursor()
    c.execute(
        "SELECT * FROM focus_sessions WHERE ended_at IS NULL ORDER BY id DESC LIMIT 1"
    )
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


# --- BACKGROUND THREAD ---

def _send_tonight_vm():
    today = date.today()
    tomorrow = today + timedelta(days=1)
    today_str = today.isoformat()
    tomorrow_str = tomorrow.isoformat()

    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT title FROM tasks WHERE status='done' AND deadline LIKE ?", (f'{today_str}%',))
    completed = [r[0] for r in c.fetchall()]
    c.execute(
        "SELECT title FROM tasks WHERE status='active' AND deadline LIKE ? AND deadline != ?",
        (f'{today_str}%', NO_DEADLINE_SENTINEL)
    )
    rolled = [r[0] for r in c.fetchall()]
    c.execute(
        "SELECT title, duration_minutes FROM tasks "
        "WHERE status='active' AND deadline LIKE ? AND deadline != ? "
        "ORDER BY deadline ASC LIMIT 3",
        (f'{tomorrow_str}%', NO_DEADLINE_SENTINEL)
    )
    tomorrow_tasks = c.fetchall()
    conn.close()

    user = get_user_name()
    msg = f"Evening briefing, {user}. "
    if completed:
        msg += f"Today you completed {len(completed)} task{'s' if len(completed) != 1 else ''}. "
        for t in completed[:3]:
            msg += f"{t}. "
    else:
        msg += "No tasks were completed today. "
    if rolled:
        msg += f"{len(rolled)} task{'s' if len(rolled) != 1 else ''} still outstanding today. "
    if tomorrow_tasks:
        msg += "Tomorrow: "
        for title, dur in tomorrow_tasks:
            msg += f"{title}"
            if dur:
                msg += f", {dur} minutes"
            msg += ". "
    evening_device = get_setting('vm_device_evening', '') or get_setting('vm_device_briefings', '')
    trigger_voice_monkey(msg, device=evening_device)


def run_evening_briefing():
    evening_time = get_setting('evening_briefing_time', '21:00')
    now = datetime.now()
    current_time = now.strftime('%H:%M')
    current_day_str = now.strftime('%a')
    briefing_days = get_setting('briefing_days', 'Mon,Tue,Wed,Thu,Fri')
    if current_time == evening_time and current_day_str in briefing_days:
        _send_tonight_vm()


def run_morning_briefing():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT key, value FROM settings WHERE key IN ('briefing_time', 'briefing_days')")
    sets = {row[0]: row[1] for row in c.fetchall()}
    now = datetime.now()
    current_time = now.strftime('%H:%M')
    current_day_str = now.strftime('%a')

    if current_time == sets.get('briefing_time') and current_day_str in sets.get('briefing_days', ''):
        c.execute(
            "SELECT title, deadline, duration_minutes FROM tasks WHERE status='active' ORDER BY deadline ASC LIMIT 5"
        )
        tasks = c.fetchall()
        conn.close()
        if not tasks:
            return
        user = get_user_name()
        quote = random.choice(MORNING_QUOTES)
        message = f"Good morning {user}. {quote} Here are your top tasks. "
        for i, task in enumerate(tasks, 1):
            title, deadline_str, duration = task
            if deadline_str == NO_DEADLINE_SENTINEL:
                message += f"Task {i}: {title}, no fixed deadline. "
                continue
            dt = datetime.strptime(deadline_str.replace('T', ' '), '%Y-%m-%d %H:%M')
            day_speak = "today" if dt.date() == now.date() else dt.strftime('%A the %d of %B')
            time_speak = dt.strftime('%H:%M')
            overdue = "overdue since" if dt < now else "due"
            dur_txt = f", estimated {duration} minutes" if duration else ""
            message += f"Task {i}: {title}, {overdue} {day_speak} at {time_speak}{dur_txt}. "
        trigger_voice_monkey(message, device=get_setting('vm_device_briefings', ''))
    else:
        conn.close()


def check_recurring():
    conn = get_db()
    c = conn.cursor()
    # Fetch all master templates
    c.execute("SELECT title, start_time, interval, end_date, duration_minutes FROM recurring_templates")
    templates = c.fetchall()
    for temp in templates:
        title, start_time, interval, end_date, tmpl_duration = temp

        # If end_date has passed, skip generating any new instances
        if end_date:
            try:
                end_dt = datetime.strptime(end_date, '%Y-%m-%d')
                if datetime.now().date() > end_dt.date():
                    continue
            except Exception:
                pass

        # We look for ANY instance of this task in the tasks table
        # If no instance exists at all, we create the first one for 'today'
        # (or the next logical occurrence)
        c.execute("SELECT deadline FROM tasks WHERE title=? ORDER BY deadline DESC LIMIT 1", (title,))
        last_instance = c.fetchone()
        if not last_instance:
            first_deadline = f"{datetime.now().strftime('%Y-%m-%d')}T{start_time}"
            c.execute("SELECT id FROM tasks WHERE title=? AND deadline=?", (title, first_deadline))
            if not c.fetchone():
                c.execute(
                    "INSERT INTO tasks (title, deadline, last_alert_type, duration_minutes, deadline_type, pin_to_date) VALUES (?, ?, 'none', ?, 'fixed', 1)",
                    (title, first_deadline, tmpl_duration or 30)
                )
    conn.commit()
    conn.close()


def maybe_generate_message_bank():
    """Generate weekly message bank if it's Monday around 2am and bank doesn't exist yet."""
    now = datetime.now()
    if now.weekday() != 0 or now.hour != 2:
        return
    today = date.today()
    monday = today - timedelta(days=today.weekday())
    week_str = monday.isoformat()

    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM message_bank WHERE week_start=?", (week_str,))
    count = c.fetchone()[0]
    conn.close()

    if count > 0:
        return

    print(f"Generating LLM message bank for week {week_str}...")
    messages = llm_service.generate_message_bank()
    if not messages:
        print("Message bank generation failed — LLM unavailable.")
        return

    conn = get_db()
    c = conn.cursor()
    for msg in messages:
        c.execute(
            "INSERT INTO message_bank (week_start, message_type, message_text) VALUES (?, ?, ?)",
            (week_str, msg['type'], msg['text'])
        )
    conn.commit()
    conn.close()
    print(f"Message bank generated: {len(messages)} messages.")


def maybe_run_gdrive_backup():
    """Run a Drive backup daily at 02:00 if authorized and backup_enabled."""
    import gdrive_backup
    if get_setting('backup_enabled', '0') != '1':
        return
    if not gdrive_backup.is_authorized():
        return
    now = datetime.now()
    if now.strftime('%H:%M') != '02:00':
        return
    last = get_setting('gdrive_last_backup', '')
    if last and last.startswith(now.strftime('%Y-%m-%d')):
        return
    try:
        fname = gdrive_backup.run_backup()
        print(f"GDrive backup complete: {fname}")
    except Exception as e:
        print(f"GDrive backup error: {e}")


# ─── Google Calendar sync ──────────────────────────────────────────────────────

_gcal_last_sync_attempt = None
_gcal_sync_lock = threading.Lock()


def run_gcal_sync():
    global _gcal_last_sync_attempt
    if get_setting('gcal_enabled', '0') != '1':
        return

    # Prevent concurrent syncs — SQLite cannot handle two writers simultaneously
    if not _gcal_sync_lock.acquire(blocking=False):
        return

    conn = None
    try:
        interval_hours = float(get_setting('gcal_sync_interval_hours', '24'))
        now = datetime.now()
        if _gcal_last_sync_attempt and (now - _gcal_last_sync_attempt).total_seconds() < interval_hours * 3600:
            return
        _gcal_last_sync_attempt = now

        import gcal_service
        import scheduler as sched_mod

        if not gcal_service.is_authorized():
            return

        busy_slots = gcal_service.fetch_busy_slots(days_ahead=21)

        conn = get_db()
        c = conn.cursor()

        c.execute("""
            SELECT id, title, duration_minutes, deadline, deadline_type, gcal_task_id, scheduled_start, pin_to_date
            FROM tasks
            WHERE status='active' AND deadline_type != 'none' AND deadline != ?
        """, (NO_DEADLINE_SENTINEL,))
        tasks = [
            {'id': r[0], 'title': r[1], 'duration_minutes': r[2],
             'deadline': r[3], 'deadline_type': r[4],
             'gcal_task_id': r[5], 'scheduled_start': r[6], 'pin_to_date': r[7]}
            for r in c.fetchall()
        ]

        # Deduplicate GCal tasks — remove any GCal task whose base title matches
        # a local task but whose ID doesn't match the stored gcal_task_id.
        # This cleans up orphaned duplicates from previous failed syncs.
        try:
            gcal_all = gcal_service.list_tasklist_tasks()
            known_ids = {t['gcal_task_id'] for t in tasks if t.get('gcal_task_id')}
            base_title_map = {}
            for gt in gcal_all:
                base = re.sub(r'\s*\[\d{2}:\d{2}-\d{2}:\d{2}\]\s*$', '', gt.get('title', '')).strip()
                base_title_map.setdefault(base, []).append(gt['id'])
            local_bases = {re.sub(r'\s*\[\d{2}:\d{2}-\d{2}:\d{2}\]\s*$', '', t['title']).strip() for t in tasks}
            for base, ids in base_title_map.items():
                if base not in local_bases:
                    continue
                for gid in ids:
                    if gid not in known_ids:
                        try:
                            gcal_service.delete_task(gid)
                        except Exception:
                            pass
        except Exception as dedup_err:
            print(f"GCal dedup warning: {dedup_err}")

        results = sched_mod.schedule_tasks(tasks, busy_slots, now=now)

        task_map = {t['id']: t for t in tasks}

        for r in results:
            task_id = r['task_id']
            task    = task_map.get(task_id, {})
            status  = r['status']

            if status == 'scheduled':
                start_str = r['scheduled_start']
                end_str   = r['scheduled_end']
                start_dt  = datetime.strptime(start_str, '%Y-%m-%dT%H:%M')
                end_dt    = datetime.strptime(end_str,   '%Y-%m-%dT%H:%M')
                gcal_title = (
                    f"{task.get('title', '')} "
                    f"[{start_dt.strftime('%H:%M')}-{end_dt.strftime('%H:%M')}]"
                )
                due_date = start_str[:10]
                existing_gcal_id = task.get('gcal_task_id') or ''

                if existing_gcal_id:
                    try:
                        gcal_service.update_task(existing_gcal_id, gcal_title, due_date)
                    except Exception as upd_err:
                        if '404' in str(upd_err):
                            # Task deleted from GCal externally — recreate
                            try:
                                new_id = gcal_service.create_task(gcal_title, due_date)
                                c.execute("UPDATE tasks SET gcal_task_id=? WHERE id=?", (new_id, task_id))
                                conn.commit()
                            except Exception as ce:
                                print(f"GCal recreate failed task {task_id}: {ce}")
                                continue
                        else:
                            print(f"GCal update error task {task_id}: {upd_err}")
                            continue
                else:
                    try:
                        new_id = gcal_service.create_task(gcal_title, due_date)
                        c.execute("UPDATE tasks SET gcal_task_id=? WHERE id=?", (new_id, task_id))
                        conn.commit()
                    except Exception as e:
                        print(f"GCal create failed task {task_id}: {e}")
                        continue

                c.execute("UPDATE tasks SET scheduled_start=?, scheduled_end=?, unschedulable=0 WHERE id=?",
                          (start_str, end_str, task_id))

            elif status == 'unschedulable':
                c.execute("UPDATE tasks SET scheduled_start=NULL, scheduled_end=NULL, unschedulable=1 WHERE id=?",
                          (task_id,))

        set_setting('gcal_last_sync', datetime.now().strftime('%Y-%m-%d %H:%M'))
        set_setting('gcal_last_sync_error', '')
        print(f"GCal sync complete — {len([r for r in results if r['status']=='scheduled'])} tasks scheduled")

    except Exception as e:
        print(f"GCal sync error: {e}")
        set_setting('gcal_last_sync_error', str(e))
    finally:
        if conn:
            conn.commit()
            conn.close()
        _gcal_sync_lock.release()


def _trigger_gcal_sync_async():
    """Reset the sync timer and kick off a GCal sync in a background thread."""
    global _gcal_last_sync_attempt
    _gcal_last_sync_attempt = None
    threading.Thread(target=run_gcal_sync, daemon=True).start()


def background_task_checker():
    import time
    while True:
        try:
            run_morning_briefing()
            run_evening_briefing()
            run_gcal_sync()
            check_recurring()
            maybe_generate_message_bank()
            maybe_run_gdrive_backup()

            conn = get_db()
            try:
                c = conn.cursor()
                c.execute("SELECT value FROM settings WHERE key='silence_mode'")
                res_silence = c.fetchone()
                silence_mode = res_silence[0] if res_silence else 'off'

                c.execute("SELECT value FROM settings WHERE key='nag_interval'")
                res_nag = c.fetchone()
                nag_interval = int(res_nag[0]) if res_nag else 15

                if silence_mode == 'off':
                    c.execute(
                        "SELECT id, title, deadline, status, last_alert_type, last_nag_time, deadline_type "
                        "FROM tasks WHERE status='active'"
                    )
                    all_tasks = c.fetchall()
                    now = datetime.now()

                    for task in all_tasks:
                        t_id, t_title, t_deadline, t_status, t_last_alert, last_nag_val, dl_type = task
                        if t_deadline == NO_DEADLINE_SENTINEL or dl_type == 'none':
                            continue

                        deadline_dt = datetime.strptime(t_deadline.replace('T', ' '), '%Y-%m-%d %H:%M')
                        time_left_mins = (deadline_dt - now).total_seconds() / 60

                        if time_left_mins <= 0:
                            should_nag = False
                            if t_last_alert in ('none', 'nag_30', 'nag_15'):
                                should_nag = True
                                new_alert_type = 'nag_expired'
                            elif t_last_alert == 'nag_expired':
                                if last_nag_val:
                                    last_nag_dt = datetime.strptime(last_nag_val, '%Y-%m-%d %H:%M:%S')
                                    if (now - last_nag_dt).total_seconds() / 60 >= nag_interval:
                                        should_nag = True
                                else:
                                    should_nag = True
                                new_alert_type = 'nag_expired'
                            else:
                                should_nag = False

                            if should_nag:
                                msg = get_message_from_bank('nag')
                                nag_text = f"{get_user_name()}. {t_title}. {msg}"
                                trigger_voice_monkey(nag_text, chime=random.choice(CHIMES))
                                c.execute(
                                    "UPDATE tasks SET last_alert_type=?, last_nag_time=? WHERE id=?",
                                    (new_alert_type, now.strftime('%Y-%m-%d %H:%M:%S'), t_id)
                                )

                        elif 0 < time_left_mins <= 15 and t_last_alert not in ('nag_15', 'nag_expired', 'nag_deadline'):
                            nag_text = f"{get_user_name()}. {t_title}. 15 minutes until deadline. {random.choice(NAG_15)}"
                            trigger_voice_monkey(nag_text, chime=random.choice(CHIMES))
                            c.execute("UPDATE tasks SET last_alert_type='nag_15' WHERE id=?", (t_id,))

                        elif 15 < time_left_mins <= 30 and t_last_alert not in ('nag_30', 'nag_15', 'nag_expired', 'nag_deadline'):
                            nag_text = f"{get_user_name()}. {t_title}. 30 minutes until deadline. {random.choice(NAG_30)}"
                            trigger_voice_monkey(nag_text, chime=random.choice(CHIMES))
                            c.execute("UPDATE tasks SET last_alert_type='nag_30' WHERE id=?", (t_id,))

                conn.commit()
            except Exception as e:
                print(f"DB error in background worker: {e}")
            finally:
                conn.close()
        except Exception as e:
            print(f"Background worker error: {e}")
        time.sleep(60)


# --- ROUTES ---

@app.errorhandler(sqlite3.OperationalError)
def handle_db_error(e):
    return (
        '<html><body style="background:#121212;color:white;font-family:sans-serif;padding:40px">'
        '<h2 style="color:#ffd700">DATABASE ERROR</h2>'
        f'<p>{e}</p>'
        '<p>On the server, run:<br>'
        '<code>df -h</code> — check disk space<br>'
        '<code>mount | grep ro</code> — check read-only filesystem<br>'
        '<code>sqlite3 ~/adhdtaskmanager/tasks.db "PRAGMA integrity_check;"</code></p>'
        '</body></html>'
    ), 503


@app.route('/')
def index():
    if get_setting('setup_complete', '0') != '1':
        return redirect('/setup')

    ua = request.headers.get('User-Agent', '').lower()
    is_mobile = any(x in ua for x in ['iphone', 'android', 'mobile'])

    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT value FROM settings WHERE key='bar_start_hours'")
    res_bar = c.fetchone()
    bar_scale_hours = float(res_bar[0]) if res_bar else 24.0
    bar_scale_mins = bar_scale_hours * 60

    c.execute("SELECT value FROM settings WHERE key='silence_mode'")
    res_silence = c.fetchone()
    silence_mode = res_silence[0] if res_silence else 'off'

    c.execute(
        "SELECT id, title, deadline, status, duration_minutes, deadline_type, scheduled_start, scheduled_end, pin_to_date "
        "FROM tasks WHERE status='active' ORDER BY deadline ASC"
    )
    all_tasks = c.fetchall()

    processed_tasks = []
    now = datetime.now()

    for task in all_tasks:
        t_id, t_title, t_deadline, t_status, dur_mins, dl_type, sched_start, sched_end, pin_to_date = task
        dur_mins = dur_mins or 30
        dl_type = dl_type or 'flexible'

        if t_deadline == NO_DEADLINE_SENTINEL or dl_type == 'none':
            processed_tasks.append({
                'id': t_id,
                'title': t_title,
                'deadline': 'NO DEADLINE',
                'percent': 0,
                'phase': 'phase-none',
                'duration_display': format_duration(dur_mins),
                'duration_minutes': dur_mins,
                'deadline_type': 'none',
                'scheduled_label': '',
                'sched_bracket': '',
                'edit_date': '',
                'edit_time': '',
                'pin_to_date': pin_to_date or 0,
            })
            continue

        deadline_dt = datetime.strptime(t_deadline.replace('T', ' '), '%Y-%m-%d %H:%M')
        time_left_mins = (deadline_dt - now).total_seconds() / 60

        if time_left_mins <= 0:
            phase = "phase-red"
        elif time_left_mins <= 15:
            phase = "phase-orange"
        elif time_left_mins <= 30:
            phase = "phase-yellow"
        else:
            phase = "phase-normal"

        percent = max(0, min(100, 100 - (time_left_mins / bar_scale_mins * 100)))
        readable_deadline = deadline_dt.strftime('%a %d %b %H:%M').upper()

        sched_bracket = ''
        sched_label = ''
        if sched_start and sched_end:
            try:
                s_dt = datetime.strptime(sched_start, '%Y-%m-%dT%H:%M')
                e_dt = datetime.strptime(sched_end,   '%Y-%m-%dT%H:%M')
                sched_bracket = f"[{s_dt.strftime('%a %d %b')} {s_dt.strftime('%H:%M')}-{e_dt.strftime('%H:%M')}]"
                sched_label   = s_dt.strftime('%d %b %H:%M').upper()
            except Exception:
                pass
        elif sched_start:
            try:
                s_dt = datetime.strptime(sched_start, '%Y-%m-%dT%H:%M')
                sched_label = s_dt.strftime('%d %b %H:%M').upper()
            except Exception:
                pass

        processed_tasks.append({
            'id': t_id,
            'title': t_title,
            'deadline': readable_deadline,
            'percent': percent,
            'phase': phase,
            'duration_display': format_duration(dur_mins),
            'duration_minutes': dur_mins,
            'deadline_type': dl_type,
            'scheduled_label': sched_label,
            'sched_bracket': sched_bracket,
            'edit_date': deadline_dt.strftime('%Y-%m-%d'),
            'edit_time': deadline_dt.strftime('%H:%M'),
            'pin_to_date': pin_to_date or 0,
        })

    c.execute("""SELECT id, title, deadline FROM tasks WHERE status='active' AND unschedulable=1""")
    unschedulable_tasks = [{'id': r[0], 'title': r[1], 'deadline': r[2]} for r in c.fetchall()]

    if is_mobile:
        conn.close()
        active_focus = _enrich_focus_session(get_active_focus_session())
        return render_template('mobile.html',
                               tasks=processed_tasks,
                               user_name=get_user_name(),
                               buffer_pct=int(get_buffer_pct()),
                               active_focus=active_focus,
                               unschedulable_tasks=unschedulable_tasks,
                               board_version=get_board_version())

    c.execute("SELECT value FROM settings WHERE key='dnd_start'")
    d_start_res = c.fetchone()
    d_start = d_start_res[0] if d_start_res else '22:00'
    c.execute("SELECT value FROM settings WHERE key='dnd_end'")
    d_end_res = c.fetchone()
    d_end = d_end_res[0] if d_end_res else '07:00'
    conn.close()

    is_dnd = _is_dnd_time(datetime.now().strftime('%H:%M'), d_start, d_end)
    active_focus = _enrich_focus_session(get_active_focus_session())

    return render_template('index.html',
                           main_tasks=processed_tasks[:5],
                           queue_tasks=processed_tasks[5:],
                           silence_mode=silence_mode,
                           dnd_active=is_dnd,
                           dnd_start=d_start,
                           dnd_end=d_end,
                           is_mobile=is_mobile,
                           active_focus=active_focus,
                           user_name=get_user_name(),
                           unschedulable_tasks=unschedulable_tasks,
                           bar_scale_mins=bar_scale_mins,
                           board_version=get_board_version())


@app.route('/api/dnd_status')
def dnd_status():
    dnd_s = get_setting('dnd_start', '22:00')
    dnd_e = get_setting('dnd_end', '07:00')
    return jsonify({
        'is_dnd': _is_dnd_time(datetime.now().strftime('%H:%M'), dnd_s, dnd_e),
        'dnd_start': dnd_s,
        'dnd_end': dnd_e,
    })


@app.route('/api/tasks')
def tasks_json():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id, title, deadline, status FROM tasks WHERE status='active' ORDER BY deadline ASC")
    tasks = c.fetchall()
    conn.close()
    return jsonify([{'id': t[0], 'title': t[1], 'deadline': t[2], 'status': t[3]} for t in tasks])


@app.route('/api/focus/start', methods=['POST'])
def focus_start():
    data = request.get_json()
    task_id = data.get('task_id')
    planned_minutes = int(data.get('planned_minutes', 30))

    # End any existing active session
    conn = get_db()
    c = conn.cursor()
    c.execute(
        "UPDATE focus_sessions SET ended_at=?, end_reason='superseded' WHERE ended_at IS NULL",
        (datetime.now().strftime('%Y-%m-%d %H:%M:%S'),)
    )

    # Get task title
    c.execute("SELECT title FROM tasks WHERE id=?", (task_id,))
    row = c.fetchone()
    task_title = row[0] if row else 'Unknown task'

    c.execute(
        "INSERT INTO focus_sessions (task_id, task_title, started_at, planned_minutes) VALUES (?, ?, ?, ?)",
        (task_id, task_title, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), planned_minutes)
    )
    session_id = c.lastrowid
    conn.commit()
    conn.close()

    # Get LLM first step
    first_step = llm_service.get_first_step(task_title)

    # Trigger engage Alexa nag
    trigger_voice_monkey(f"{get_user_name()}. Focus mode started. {task_title}. Let's go.", device=get_setting('vm_device_focus', ''))

    return jsonify({
        'status': 'ok',
        'session_id': session_id,
        'task_title': task_title,
        'planned_minutes': planned_minutes,
        'first_step': first_step,
    })


@app.route('/api/focus/end', methods=['POST'])
def focus_end():
    data = request.get_json()
    reason = data.get('reason', 'cancelled')  # 'completed', 'cancelled', 'expired'
    session_id = data.get('session_id')
    task_id = data.get('task_id')

    conn = get_db()
    c = conn.cursor()
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    c.execute(
        "UPDATE focus_sessions SET ended_at=?, end_reason=? WHERE ended_at IS NULL",
        (now_str, reason)
    )
    conn.commit()
    conn.close()

    if reason in ('complete', 'completed') and task_id:
        return complete_task_internal(task_id)

    return jsonify({'status': 'ok', 'reason': reason})


@app.route('/api/focus/break_reminder', methods=['POST'])
def focus_break_reminder():
    data = request.get_json()
    task_title = data.get('task_title', 'your task')
    mins_remaining = data.get('mins_remaining', 0)

    user = get_user_name()
    if mins_remaining <= 2:
        msg = f"{user}. Two minutes remaining on {task_title}. Start wrapping up."
    else:
        msg = f"{user}. Take a quick break. Drink some water, have a stretch, take a moment."

    trigger_voice_monkey(msg, device=get_setting('vm_device_focus', ''))
    return jsonify({'status': 'ok'})


@app.route('/api/focus/expired', methods=['POST'])
def focus_expired():
    data = request.get_json()
    task_title = data.get('task_title', 'your task')
    escalation = data.get('escalation', 1)

    user = get_user_name()
    nag_messages = [
        f"{user}. Time's up on {task_title}. Are you done yet?",
        f"{user}. {task_title}. Still going? The clock says otherwise.",
        f"{user}. {task_title}. {random.choice(NAG_EXPIRED)}",
        f"{user}. {random.choice(NAG_DEADLINE)}",
    ]
    idx = min(escalation - 1, len(nag_messages) - 1)
    trigger_voice_monkey(nag_messages[idx], device=get_setting('vm_device_focus', ''), chime=random.choice(CHIMES))
    return jsonify({'status': 'ok'})


@app.route('/api/focus/nudge', methods=['POST'])
def focus_nudge():
    data = request.get_json(silent=True) or {}
    mins = int(data.get('mins_remaining', 0))
    msg = f"{get_user_name()}. {mins} minutes remaining." if mins > 0 else f"{get_user_name()}. Stay focused."
    trigger_voice_monkey(msg, device=get_setting('vm_device_focus', ''))
    return jsonify({'status': 'ok', 'nudge': msg})


@app.route('/api/estimate_duration', methods=['POST'])
def estimate_duration_api():
    data = request.get_json()
    task_title = data.get('title', '')
    if not task_title:
        return jsonify({'error': 'No title provided'}), 400

    buffer_pct = get_buffer_pct()
    result = llm_service.estimate_duration(task_title, buffer_pct)
    if not result:
        return jsonify({'error': 'LLM unavailable'}), 503

    raw, buffered, rationale = result
    return jsonify({
        'raw_minutes': raw,
        'buffered_minutes': buffered,
        'buffer_pct': buffer_pct,
        'rationale': rationale,
        'display': format_duration(buffered),
    })


@app.route('/api/test_llm', methods=['POST'])
def test_llm_api():
    data = request.get_json(silent=True, force=True) or {}
    overrides = {
        'provider': data.get('provider', ''),
        'quick_model': data.get('quick_model', ''),
        'deep_model': data.get('deep_model', ''),
        'api_key': data.get('api_key', ''),
        'ollama_host': data.get('ollama_host', ''),
    }
    success, message = llm_service.test_connection(overrides=overrides)
    return jsonify({'success': success, 'message': message})


@app.route('/gcal_auth_redirect')
def gcal_auth_redirect():
    import gcal_service
    redirect_uri = f"http://localhost:{_get_app_port()}/gcal_callback"
    auth_url = gcal_service.get_auth_url(redirect_uri)
    return redirect(auth_url)


@app.route('/gcal_callback')
def gcal_callback():
    import gcal_service
    code = request.args.get('code')
    error = request.args.get('error')
    if error or not code:
        return redirect('/settings?gcal_error=access_denied')
    try:
        redirect_uri = f"http://localhost:{_get_app_port()}/gcal_callback"
        gcal_service.exchange_code(code, redirect_uri)
        set_setting('gcal_enabled', '1')
        return redirect('/settings?gcal_success=1')
    except Exception as e:
        print(f"GCal OAuth error: {e}")
        return redirect('/settings?gcal_error=token_exchange')


@app.route('/gcal_disconnect', methods=['POST'])
def gcal_disconnect():
    import gcal_service
    gcal_service.disconnect()
    set_setting('gcal_enabled', '0')
    return redirect('/settings')


# ─── Google Drive Backup OAuth ────────────────────────────────────────────────

@app.route('/gdrive_backup_auth_redirect')
def gdrive_backup_auth_redirect():
    import gdrive_backup
    redirect_uri = f"http://localhost:{_get_app_port()}/gdrive_backup_callback"
    return redirect(gdrive_backup.get_auth_url(redirect_uri))


@app.route('/gdrive_backup_callback')
def gdrive_backup_callback():
    import gdrive_backup
    code = request.args.get('code')
    error = request.args.get('error')
    if error or not code:
        return redirect('/settings?gdrive_error=access_denied')
    try:
        redirect_uri = f"http://localhost:{_get_app_port()}/gdrive_backup_callback"
        gdrive_backup.exchange_code(code, redirect_uri)
        return redirect('/settings?gdrive_success=1')
    except Exception as e:
        print(f"GDrive backup OAuth error: {e}")
        return redirect('/settings?gdrive_error=token_exchange')


@app.route('/gdrive_backup_disconnect', methods=['POST'])
def gdrive_backup_disconnect():
    import gdrive_backup
    gdrive_backup.disconnect()
    return redirect('/settings')


@app.route('/api/gdrive_backup_status')
def gdrive_backup_status():
    import gdrive_backup
    return jsonify({
        'authorized':  gdrive_backup.is_authorized(),
        'last_backup': get_setting('gdrive_last_backup', 'Never'),
    })


@app.route('/api/gdrive_backup_now', methods=['POST'])
def gdrive_backup_now():
    import gdrive_backup
    if not gdrive_backup.is_authorized():
        return jsonify({'success': False, 'message': 'Not authorized'})
    try:
        fname = gdrive_backup.run_backup()
        return jsonify({'success': True, 'filename': fname,
                        'last_backup': get_setting('gdrive_last_backup', '')})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/gcal_sync_now', methods=['POST'])
def gcal_sync_now():
    global _gcal_last_sync_attempt
    _gcal_last_sync_attempt = None  # Force sync regardless of interval
    set_setting('gcal_last_sync_error', '')
    try:
        run_gcal_sync()
        error = get_setting('gcal_last_sync_error', '')
        if error:
            return jsonify({'success': False, 'error': error})
        last = get_setting('gcal_last_sync', '')
        return jsonify({'success': True, 'last_sync': last})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


def get_board_version():
    """A lightweight version string for the active task set — changes on task add/complete/edit."""
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT COUNT(*), COALESCE(MAX(id), 0), COALESCE(SUM(percent), 0) FROM tasks WHERE status='active'")
    count, max_id, sum_pct = c.fetchone()
    conn.close()
    return f"{count}-{max_id}-{sum_pct}"


@app.route('/api/board_version')
def board_version():
    return jsonify({"v": get_board_version()})


@app.route('/api/gcal_status')
def gcal_status():
    import gcal_service
    return jsonify({
        'authorized':    gcal_service.is_authorized(),
        'enabled':       get_setting('gcal_enabled', '0') == '1',
        'last_sync':     get_setting('gcal_last_sync', 'Never'),
        'sync_interval': get_setting('gcal_sync_interval_hours', '24'),
        'last_error':    get_setting('gcal_last_sync_error', ''),
    })


def _get_app_port():
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT value FROM settings WHERE key='port'")
        res = c.fetchone()
        conn.close()
        return int(res[0]) if res else 5001
    except Exception:
        return 5001


@app.route('/api/quick_add_parse', methods=['POST'])
def quick_add_parse():
    data = request.get_json()
    text = data.get('text', '')
    if not text:
        return jsonify({'error': 'No text provided'}), 400

    result = llm_service.parse_natural_language_task(text)
    if not result:
        return jsonify({'error': 'LLM unavailable'}), 503

    # Apply buffer to duration if present
    if result.get('duration_minutes'):
        buf = get_buffer_pct()
        raw = result['duration_minutes']
        result['duration_minutes'] = max(5, round(raw * (1 + buf / 100) / 5) * 5)

    return jsonify(result)


@app.route('/api/tonight')
def tonight_api():
    today = date.today()
    tomorrow = today + timedelta(days=1)
    today_str = today.isoformat()
    tomorrow_str = tomorrow.isoformat()

    conn = get_db()
    c = conn.cursor()

    # Tasks completed today
    c.execute(
        "SELECT title FROM tasks WHERE status='done' AND deadline LIKE ?",
        (f'{today_str}%',)
    )
    completed = [r[0] for r in c.fetchall()]

    # Active tasks that were due today but not done (rolled over)
    c.execute(
        "SELECT title FROM tasks WHERE status='active' AND deadline LIKE ? AND deadline != ?",
        (f'{today_str}%', NO_DEADLINE_SENTINEL)
    )
    rolled = [r[0] for r in c.fetchall()]

    # Tomorrow's top 5
    c.execute(
        "SELECT title, duration_minutes, deadline_type FROM tasks "
        "WHERE status='active' AND deadline LIKE ? AND deadline != ? "
        "ORDER BY deadline ASC LIMIT 5",
        (f'{tomorrow_str}%', NO_DEADLINE_SENTINEL)
    )
    tomorrow_tasks = [{'title': r[0], 'duration': format_duration(r[1]), 'type': r[2]} for r in c.fetchall()]

    # Also include no-deadline tasks as potential tomorrow items (up to 3)
    c.execute(
        "SELECT title, duration_minutes FROM tasks "
        "WHERE status='active' AND deadline_type='none' ORDER BY id ASC LIMIT 3"
    )
    backlog_tasks = [{'title': r[0], 'duration': format_duration(r[1]), 'type': 'none'} for r in c.fetchall()]

    conn.close()

    return jsonify({
        'completed_today': completed,
        'rolled_over': rolled,
        'tomorrow_tasks': tomorrow_tasks,
        'backlog_preview': backlog_tasks,
        'tomorrow_day': tomorrow.strftime('%A'),
    })


_FALLBACK_QUESTIONS = [
    {"question": "Does this task require input or approval from anyone else?", "options": ["Yes", "No"]},
    {"question": "Do you have everything you need to start right now?", "options": ["Yes, ready to go", "No, need to gather things first"]},
    {"question": "Is this something you've done before?", "options": ["Yes, I know the process", "No, it's new to me"]},
    {"question": "Will any parts need to happen in a specific order?", "options": ["Yes, strict order", "No, can do in any order"]},
    {"question": "Are there any parts that depend on other things completing first?", "options": ["Yes", "No"]},
]

@app.route('/api/breakdown/questions', methods=['POST'])
def breakdown_questions():
    data = request.get_json()
    task_title = data.get('title', '')
    questions = llm_service.generate_breakdown_questions(task_title) or _FALLBACK_QUESTIONS
    return jsonify({'questions': questions, 'title': task_title})


@app.route('/api/breakdown/complete', methods=['POST'])
def breakdown_complete():
    data = request.get_json()
    task_title = data.get('title', '')
    deadline = data.get('deadline', '')
    answers = data.get('answers', {})

    subtasks = llm_service.breakdown_complex_task(task_title, deadline, answers)
    if not subtasks:
        return jsonify({'error': 'LLM unavailable or no subtasks generated'}), 503

    buffer_pct = get_buffer_pct()
    for s in subtasks:
        raw = s.get('duration_minutes', 30)
        s['duration_minutes'] = max(5, round(raw * (1 + buffer_pct / 100) / 5) * 5)
        s['duration_display'] = format_duration(s['duration_minutes'])

    return jsonify({'subtasks': subtasks})


@app.route('/api/breakdown/commit', methods=['POST'])
def breakdown_commit():
    data = request.get_json()
    parent_title = data.get('parent_title', '')
    parent_deadline = data.get('parent_deadline', NO_DEADLINE_SENTINEL)
    subtasks = data.get('subtasks', [])

    conn = get_db()
    c = conn.cursor()

    # Create parent task
    c.execute(
        "INSERT INTO tasks (title, deadline, last_alert_type, deadline_type, duration_minutes) "
        "VALUES (?, ?, 'none', 'flexible', ?)",
        (f"[PARENT] {parent_title}", parent_deadline, 0)
    )
    parent_id = c.lastrowid

    for s in subtasks:
        dl_date = s.get('deadline_date', '')
        dl_time = s.get('deadline_time', '09:00')
        if dl_date:
            deadline = f"{dl_date}T{dl_time}"
            dl_type = 'flexible'
        else:
            deadline = NO_DEADLINE_SENTINEL
            dl_type = 'none'
        c.execute(
            "INSERT INTO tasks (title, deadline, last_alert_type, deadline_type, duration_minutes, parent_task_id) "
            "VALUES (?, ?, 'none', ?, ?, ?)",
            (s['title'], deadline, dl_type, s.get('duration_minutes', 30), parent_id)
        )

    conn.commit()
    conn.close()
    if get_setting('gcal_enabled', '0') == '1':
        _trigger_gcal_sync_async()
    return jsonify({'status': 'ok', 'parent_id': parent_id, 'count': len(subtasks)})


@app.route('/toggle_silence', methods=['POST'])
def toggle_silence():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT value FROM settings WHERE key='silence_mode'")
    res = c.fetchone()
    current = res[0] if res else 'off'
    new_val = 'on' if current == 'off' else 'off'
    c.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('silence_mode', ?)", (new_val,))
    conn.commit()
    conn.close()
    return jsonify({"status": "success", "mode": new_val})


@app.route('/add', methods=['GET', 'POST'])
def add_task():
    if request.method == 'POST':
        task_type = request.form.get('type')
        title = request.form.get('title', '').strip()
        if not title:
            return "Error: Title is compulsory.", 400

        duration_minutes = request.form.get('duration_minutes') or request.form.get('duration_minutes_recur', '30')
        try:
            duration_minutes = int(duration_minutes)
        except Exception:
            duration_minutes = 30

        already_buffered = request.form.get('duration_already_buffered') == '1'
        deadline_type = request.form.get('deadline_type', 'flexible')
        pin_to_date = 1 if request.form.get('pin_to_date') else 0

        conn = get_db()
        c = conn.cursor()
        try:
            if task_type == 'recurring':
                interval = request.form.get('interval')
                recur_time = request.form.get('recur_time')
                recur_start_date = request.form.get('recur_start_date')
                recur_end_date = request.form.get('recur_end_date', '').strip()
                if not all([interval, recur_time, recur_start_date]):
                    return "Error: All recurring fields are compulsory.", 400
                if '-' in recur_start_date:
                    iso_start_date = recur_start_date
                else:
                    day, month, year = recur_start_date.split('/')
                    iso_start_date = f"{year}-{month}-{day}"

                # Parse optional end date
                iso_end_date = None
                if recur_end_date:
                    if '-' in recur_end_date:
                        iso_end_date = recur_end_date
                    else:
                        ed, em, ey = recur_end_date.split('/')
                        iso_end_date = f"{ey}-{em}-{ed}"

                buf = get_buffer_pct()
                buffered_duration = max(5, round(duration_minutes * (1 + buf / 100) / 5) * 5)
                now_today = datetime.now().strftime('%Y-%m-%d')
                c.execute(
                    "INSERT INTO recurring_templates (title, start_time, interval, last_generated, end_date, duration_minutes) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (title, recur_time, interval, now_today, iso_end_date, buffered_duration)
                )
                first_deadline = f"{iso_start_date}T{recur_time}"
                c.execute(
                    "INSERT INTO tasks (title, deadline, last_alert_type, duration_minutes, deadline_type, pin_to_date) "
                    "VALUES (?, ?, 'none', ?, 'fixed', 1)",
                    (title, first_deadline, buffered_duration)
                )
            else:
                if not already_buffered:
                    buf = get_buffer_pct()
                    duration_minutes = max(5, round(duration_minutes * (1 + buf / 100) / 5) * 5)

                if deadline_type == 'none':
                    deadline = NO_DEADLINE_SENTINEL
                else:
                    uk_date = request.form.get('deadline_date')
                    d_time = request.form.get('deadline_time')
                    if not all([uk_date, d_time]):
                        return "Error: Date and time are required unless No Deadline is selected.", 400
                    if '-' in uk_date:
                        iso_date = uk_date
                    else:
                        day, month, year = uk_date.split('/')
                        iso_date = f"{year}-{month}-{day}"
                    deadline = f"{iso_date}T{d_time}"

                c.execute(
                    "INSERT INTO tasks (title, deadline, last_alert_type, duration_minutes, deadline_type, pin_to_date) "
                    "VALUES (?, ?, 'none', ?, ?, ?)",
                    (title, deadline, duration_minutes, deadline_type, pin_to_date)
                )

            conn.commit()
            conn.close()
            if get_setting('gcal_enabled', '0') == '1':
                _trigger_gcal_sync_async()
            return redirect('/')
        except Exception as e:
            conn.close()
            return f"Error: {e}. Go back and check your data format.", 400

    ua = request.headers.get('User-Agent', '').lower()
    is_mobile = any(x in ua for x in ['iphone', 'android', 'mobile'])
    buffer_pct = get_buffer_pct()
    return render_template('add.html', is_mobile=is_mobile, buffer_pct=int(buffer_pct))


def complete_task_internal(task_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT title, deadline, gcal_task_id FROM tasks WHERE id=?", (task_id,))
    task = c.fetchone()
    if not task:
        conn.close()
        return jsonify({"status": "error"}), 404

    title, current_deadline, gcal_task_id = task
    c.execute("UPDATE tasks SET status='done' WHERE id=?", (task_id,))

    # Handle recurring — generate next instance synchronously so the board updates immediately
    c.execute("SELECT interval, end_date, duration_minutes FROM recurring_templates WHERE title=?", (title,))
    template = c.fetchone()
    if template and current_deadline != NO_DEADLINE_SENTINEL:
        interval, end_date, tmpl_duration = template
        old_dt = datetime.strptime(current_deadline.replace('T', ' '), '%Y-%m-%d %H:%M')
        if interval == 'weekly':
            count, unit = 1, 'W'
        elif interval == 'daily':
            count, unit = 1, 'D'
        elif interval == 'monthly':
            count, unit = 1, 'M'
        else:
            count = int(interval[:-1])
            unit = interval[-1]

        if unit == 'D':
            new_dt = old_dt + timedelta(days=count)
        elif unit == 'W':
            new_dt = old_dt + timedelta(weeks=count)
        elif unit == 'M':
            new_dt = old_dt
            for _ in range(count):
                month = new_dt.month % 12 + 1
                year = new_dt.year + (new_dt.month // 12)
                day = min(new_dt.day, calendar.monthrange(year, month)[1])
                new_dt = new_dt.replace(year=year, month=month, day=day)

        new_deadline = new_dt.strftime('%Y-%m-%dT%H:%M')

        past_end = False
        if end_date:
            try:
                end_dt = datetime.strptime(end_date, '%Y-%m-%d')
                past_end = new_dt.date() > end_dt.date()
            except Exception:
                past_end = False

        if not past_end:
            c.execute("SELECT id FROM tasks WHERE title=? AND deadline=?", (title, new_deadline))
            if not c.fetchone():
                c.execute(
                    "INSERT INTO tasks (title, deadline, last_alert_type, duration_minutes, deadline_type, pin_to_date) VALUES (?, ?, 'none', ?, 'fixed', 1)",
                    (title, new_deadline, tmpl_duration or 30)
                )

    conn.commit()
    conn.close()

    # Celebration
    if current_deadline != NO_DEADLINE_SENTINEL:
        deadline_dt = datetime.strptime(current_deadline.replace('T', ' '), '%Y-%m-%d %H:%M')
        is_late = datetime.now() > deadline_dt
    else:
        is_late = False

    msg = get_message_from_bank('praise')
    user = get_user_name()
    if is_late:
        vm_msg = random.choice(LATE_PRAISE_MESSAGES).format(name=user)
    else:
        vm_msg = msg if '{name}' not in msg else msg.format(name=user)

    selected_theme = random.choice(['matrix', 'glitch', 'gold-rush', 'fireworks', 'confetti'])
    applause_num = random.randint(1, 8)
    audio_url = f"/soundfx/applause{applause_num}.mp3"

    # Fire GCal complete and VM announcement in background — don't block the response
    def _bg(_gcal_id=gcal_task_id, _t=title, _dl=current_deadline, _msg=vm_msg):
        if get_setting('gcal_enabled', '0') == '1':
            try:
                import gcal_service as _gcal_svc
                if _gcal_id:
                    _gcal_svc.complete_task(_gcal_id)
                else:
                    due_str = (_dl[:10] if _dl and NO_DEADLINE_SENTINEL not in _dl else date.today().isoformat())
                    new_gcal_id = _gcal_svc.create_task(_t, due_str)
                    _gcal_svc.complete_task(new_gcal_id)
                    bg_conn = get_db()
                    bg_conn.execute("UPDATE tasks SET gcal_task_id=? WHERE id=?", (new_gcal_id, task_id))
                    bg_conn.commit()
                    bg_conn.close()
            except Exception as e:
                print(f"GCal bg complete failed for task {task_id}: {e}")
        trigger_voice_monkey(_msg)

    threading.Thread(target=_bg, daemon=True).start()

    return jsonify({
        "status": "success",
        "message": vm_msg,
        "theme": selected_theme,
        "audio": audio_url,
    })


@app.route('/complete/<int:task_id>', methods=['POST'])
def complete_task(task_id):
    return complete_task_internal(task_id)


@app.route('/recovery')
def recovery():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id, title, deadline FROM tasks WHERE status='done' ORDER BY id DESC LIMIT 20")
    rows = c.fetchall()
    processed_recovery = []
    for r in rows:
        t_id, title, deadline_str = r
        if deadline_str == NO_DEADLINE_SENTINEL:
            uk_format = 'NO DEADLINE'
        else:
            dt = datetime.strptime(deadline_str.replace('T', ' '), '%Y-%m-%d %H:%M')
            uk_format = dt.strftime('%A, %d %b %Y %H:%M').upper()
        processed_recovery.append({'id': t_id, 'title': title, 'was_due': uk_format})
    conn.close()
    return render_template('recovery.html', tasks=processed_recovery)


@app.route('/restore/<int:task_id>', methods=['POST'])
def restore_task(task_id):
    conn = get_db()
    c = conn.cursor()
    c.execute(
        "UPDATE tasks SET status='active', last_alert_type='none', last_nag_time=NULL WHERE id=?",
        (task_id,)
    )
    conn.commit()
    conn.close()
    return redirect('/')


@app.route('/manage_recurring')
def manage_recurring():
    conn = get_db()
    c = conn.cursor()
    # Fetch templates
    c.execute("SELECT id, title, start_time, interval, end_date FROM recurring_templates")
    rows = c.fetchall()
    processed_templates = []
    for r in rows:
        t_id, title, s_time, interval, end_date = r

        # Look up the first task created for this title to get the original date
        c.execute("SELECT deadline FROM tasks WHERE title=? ORDER BY id ASC LIMIT 1", (title,))
        task_res = c.fetchone()
        display_str = ""
        if task_res:
            dt = datetime.strptime(task_res[0].replace('T', ' '), '%Y-%m-%d %H:%M')
            if interval == 'weekly':
                count, unit = 1, 'W'
            elif interval == 'daily':
                count, unit = 1, 'D'
            elif interval == 'monthly':
                count, unit = 1, 'M'
            else:
                count = int(interval[:-1])
                unit = interval[-1]
            if unit == 'D':
                display_str = f"EVERY {count} DAYS @ {s_time}" if count > 1 else f"DAILY @ {s_time}"
            elif unit == 'W':
                day_name = dt.strftime('%A').upper()
                display_str = f"EVERY {count} WEEKS ({day_name}) @ {s_time}" if count > 1 else f"EVERY {day_name} @ {s_time}"
            elif unit == 'M':
                day_num = dt.day
                suffix = {1: 'ST', 2: 'ND', 3: 'RD'}.get(day_num % 10, 'TH')
                if 11 <= day_num <= 13:
                    suffix = 'TH'
                display_str = f"EVERY {count} MONTHS (ON THE {day_num}{suffix}) @ {s_time}" if count > 1 else f"EVERY {day_num}{suffix} OF THE MONTH @ {s_time}"

            # Format end date for display
            end_display = None
            if end_date:
                try:
                    end_dt = datetime.strptime(end_date, '%Y-%m-%d')
                    end_display = end_dt.strftime('%d %b %Y').upper()
                except Exception:
                    end_display = end_date

            processed_templates.append({
                'id': t_id,
                'title': title,
                'display': display_str,
                'end_date': end_display
            })
    conn.close()
    return render_template('manage_recurring.html', templates=processed_templates)


@app.route('/delete_template/<int:t_id>', methods=['POST'])
def delete_template(t_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("DELETE FROM recurring_templates WHERE id=?", (t_id,))
    conn.commit()
    conn.close()
    return redirect('/manage_recurring')


@app.route('/settings', methods=['GET', 'POST'])
def settings():
    conn = get_db()
    c = conn.cursor()

    if request.method == 'POST':
        setting_keys = [
            'briefing_time', 'evening_briefing_time', 'dnd_start', 'dnd_end', 'bar_start_hours',
            'nag_interval', 'port', 'adhd_buffer_pct',
            'llm_provider', 'llm_quick_model', 'llm_deep_model', 'llm_api_key',
            'llm_ollama_host', 'user_name',
            'gcal_enabled', 'gcal_sync_interval_hours',
            'gcal_client_id', 'gcal_client_secret',
            'vm_enabled', 'vm_token', 'vm_device_alerts', 'vm_device_briefings',
            'vm_device_evening', 'vm_device_focus', 'vm_language',
            'backup_enabled', 'gdrive_client_id', 'gdrive_client_secret',
        ]
        for key in setting_keys:
            val = request.form.get(key)
            if val is not None:
                c.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, val))

        selected_days = request.form.getlist('briefing_days')
        days_string = ",".join(selected_days)
        c.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", ('briefing_days', days_string))

        conn.commit()
        conn.close()
        return redirect('/')

    c.execute("SELECT key, value FROM settings")
    rows = c.fetchall()
    current_settings = {row[0]: row[1] for row in rows}
    conn.close()
    return render_template('settings.html', settings=current_settings)


@app.route('/edit_list')
def edit_list():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id, title, deadline FROM tasks WHERE status='active' ORDER BY deadline ASC")
    tasks = c.fetchall()
    conn.close()
    processed = [{'id': t[0], 'title': t[1], 'deadline': t[2]} for t in tasks]
    return render_template('edit_list.html', tasks=processed)


@app.route('/edit/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    conn = get_db()
    c = conn.cursor()

    if request.method == 'POST':
        new_title = request.form.get('title', '').strip()
        uk_date = request.form.get('deadline_date')
        d_time = request.form.get('deadline_time')
        deadline_type = request.form.get('deadline_type', 'flexible')
        duration_minutes = request.form.get('duration_minutes', '30')
        pin_to_date = 1 if request.form.get('pin_to_date') else 0
        try:
            duration_minutes = int(duration_minutes)
        except Exception:
            duration_minutes = 30

        if deadline_type == 'none':
            deadline = NO_DEADLINE_SENTINEL
        else:
            if not all([uk_date, d_time]):
                return "Error: All fields are compulsory.", 400
            if '-' in uk_date:
                iso_date = uk_date
            else:
                day, month, year = uk_date.split('/')
                iso_date = f"{year}-{month}-{day}"
            deadline = f"{iso_date}T{d_time}"

        if new_title:
            c.execute(
                "UPDATE tasks SET title=?, deadline=?, last_alert_type='none', last_nag_time=NULL, "
                "duration_minutes=?, deadline_type=?, scheduled_start=NULL, scheduled_end=NULL, pin_to_date=? WHERE id=?",
                (new_title, deadline, duration_minutes, deadline_type, pin_to_date, task_id)
            )
        else:
            c.execute(
                "UPDATE tasks SET deadline=?, last_alert_type='none', last_nag_time=NULL, "
                "duration_minutes=?, deadline_type=?, scheduled_start=NULL, scheduled_end=NULL, pin_to_date=? WHERE id=?",
                (deadline, duration_minutes, deadline_type, pin_to_date, task_id)
            )
        conn.commit()
        conn.close()
        if get_setting('gcal_enabled', '0') == '1':
            _trigger_gcal_sync_async()
        return redirect('/')

    c.execute("SELECT id, title, deadline, duration_minutes, deadline_type, pin_to_date FROM tasks WHERE id=?", (task_id,))
    task = c.fetchone()
    conn.close()

    if not task:
        return "Task not found", 404

    t_id, title, deadline_str, dur, dl_type, pin_to_date = task
    if deadline_str == NO_DEADLINE_SENTINEL or dl_type == 'none':
        date_val = ''
        time_val = ''
        dl_type = 'none'
    else:
        dt = datetime.strptime(deadline_str.replace('T', ' '), '%Y-%m-%d %H:%M')
        date_val = dt.strftime('%d/%m/%Y')
        time_val = dt.strftime('%H:%M')

    return render_template('edit_task.html', task={
        'id': t_id,
        'title': title,
        'date': date_val,
        'time': time_val,
        'duration_minutes': dur or 30,
        'deadline_type': dl_type or 'flexible',
        'pin_to_date': pin_to_date or 0,
    })


@app.route('/media/<path:filename>')
def serve_media(filename):
    media_path = os.path.join(os.path.dirname(__file__), 'media')
    return send_from_directory(media_path, filename)


@app.route('/soundfx/<path:filename>')
def serve_soundfx(filename):
    soundfx_path = os.path.join(os.path.dirname(__file__), 'soundfx')
    return send_from_directory(soundfx_path, filename)


@app.route('/setup', methods=['GET', 'POST'])
def setup():
    if request.method == 'POST':
        choice = request.form.get('backup_choice')
        if not choice:
            return "Error: Backup choice is compulsory.", 400
        set_setting('setup_complete', '1')
        if choice == 'yes':
            return redirect('/setup_oauth')
        return redirect('/')
    return render_template('setup_backup.html')


@app.route('/setup_oauth', methods=['GET', 'POST'])
def setup_oauth():
    if request.method == 'POST':
        client_id = request.form.get('client_id')
        client_secret = request.form.get('client_secret')
        if not all([client_id, client_secret]):
            return "Error: All fields are compulsory.", 400
        set_setting('setup_complete', '1')
        set_setting('gdrive_client_id', client_id)
        set_setting('gdrive_client_secret', client_secret)
        return redirect('/')
    return render_template('setup_oauth.html')


@app.route('/nuke', methods=['POST'])
def nuke():
    def _shutdown():
        import time
        time.sleep(0.4)
        try:
            subprocess.Popen(['pkill', 'chromium'])
        except Exception:
            pass
        os.kill(os.getpid(), signal.SIGTERM)
    threading.Thread(target=_shutdown, daemon=True).start()
    return jsonify({'ok': True})


if __name__ == '__main__':
    init_db()

    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    c.execute("SELECT value FROM settings WHERE key='port'")
    res = c.fetchone()
    app_port = int(res[0]) if res else 5001
    conn.close()

    if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        t = threading.Thread(target=background_task_checker, daemon=True)
        t.start()

    import logging
    logging.getLogger('werkzeug').setLevel(logging.ERROR)
    app.run(host='0.0.0.0', port=app_port, debug=True)
