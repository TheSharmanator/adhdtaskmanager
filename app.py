import sqlite3
import requests
import random
from flask import Flask, render_template, request, redirect, jsonify, send_from_directory
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

import json
import os

# --- CONFIGURATION ---
config_path = os.path.join(os.path.dirname(__file__), 'config.json')
with open(config_path) as f:
    config = json.load(f)
    VM_ENABLED = config.get('VM', False)
    VM_TOKEN = config.get('VM_TOKEN', '')
    VM_DEVICE_ALERTS = config.get('VM_DEVICE_ALERTS', '')
    VM_DEVICE_BRIEFINGS = config.get('VM_DEVICE_BRIEFINGS', '')
    VM_LANGUAGE = config.get('VM_LANGUAGE', 'en-GB')
    USER_NAME = config.get('USER_NAME', 'Joe')

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
    "The only person you should try to be better than is the person you were yesterday.",
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
    "The countdown is getting loud.",
    "End of the line is approaching.",
    "Pull your finger out.",
    "Just half an hour left.",
    "Do you hear that? It's the sound of failure looming.",
    "Clocking off soon, finish up.",
    "Don't leave it to the last second.",
    "Start the final sprint.",
    "Time is a luxury you've run out of.",
    "Last bit of gas in the tank, use it.",
    "Stop daydreaming and start finishing.",
    "This is your 1800-second warning.",
    "You're flirting with disaster.",
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
    "You're staring down the barrel of a failure.",
    "Engage or evaporate.",
    "Shift it. Now.",
    "The fuse is down to the last inch.",
    "The grace period is dead.",
    "Finish it or face the music.",
    "Don't you dare stop moving.",
    "The pressure is on. Deal with it.",
    "Final sprint. No more talking.",
    "You're flirting with a total collapse.",
    "I want results, not sweat.",
    "It's now or never, and 'now' is nearly gone.",
    "The guillotine is dropping.",
    "Blood, sweat, and gears. Go.",
    "Fifteen minutes. Make them count.",
    "There is no more 'later'.",
    "You're playing with fire and you're about to get burned.",
    "Don't look up until it's finished.",
    "The countdown is deafening.",
    "Hustle. Fast.",
    "The cliff edge is under your feet.",
    "Whatever you're doing, do it twice as fast.",
    "This is the end of the line.",
    "No excuses will save you in fifteen minutes.",
    "Panic later. Work now.",
    "The sand has practically run out.",
    "Speed is the only thing that matters.",
    "You're on the edge of a catastrophe.",
    "Shut up and finish.",
    "The bells are ringing.",
    "This is your final, final warning.",
    "Put the hammer down.",
    "The window has slammed shut.",
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
    "You've traded your reputation for a bit of daydreaming.",
    "The time for excuses expired sixty seconds ago.",
    "Staring at the wreckage of a missed chance.",
    "You've failed the most basic requirement: finishing.",
    "The lights are off and the doors are barred.",
    "A masterclass in how to fail.",
    "The countdown reached zero and you blinked.",
    "Everything's gone cold.",
    "You had the tools, the time, and the warnings.",
    "Total silence on the delivery front.",
    "The cliff edge is behind you now. You're in freefall.",
    "The final warning was exactly that, final.",
    "The moment has passed and you weren't in it.",
    "The sand has run out, and so has my patience.",
    "Whatever you've got now is too little, too late.",
    "A spectacular display of inertia.",
    "The game was yours to lose, and you lost it.",
    "You've left it all on the table, and the table's being cleared.",
    "The clock is mocking you now.",
    "The deadline didn't fail you; you failed the deadline.",
    "The end of the line. You didn't make the distance.",
    "Wrap it up. It's a corpse now.",
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
    "The sand is gone, the glass is smashed, and the table's been sold.",
    "Are we waiting for a miracle or just a pulse?",
    "The silence on this is getting loud.",
    "We've reached the 'why bother' stage.",
    "You're dragging an anchor through a desert.",
    "The lights went out a long time ago.",
    "This isn't a struggle; it's a surrender.",
    "Still at the starting line while the crowd has gone home.",
    "The expiry date wasn't a suggestion.",
    "Wasting time on a corpse.",
    "The window of relevance has been boarded up.",
    "We're digging a hole for a job that's already buried.",
    "Beyond late. Beyond excuses.",
    "The reaper has grown old waiting for this.",
    "Total system failure.",
    "A complete and utter lack of momentum.",
    "The countdown hit zero and then kept going into the negatives.",
    "It's a ghost ship. No one's at the helm.",
    "You've turned a task into a legend of procrastination.",
    "The world moved on; you didn't.",
    "Looking at the wreckage of what could have been.",
    "This is a slow-motion car crash without the motion.",
    "The bells stopped tolling because they gave up.",
    "We're in the 'afterlife' of this deadline.",
    "Your reputation is currently in the bin.",
    "A void where effort used to live.",
    "The deadline is ancient history.",
    "Is there anyone actually in there?",
    "You've missed the boat, the train, and the point.",
    "The smell of failure is getting ripe.",
    "This is a spectacular display of nothingness.",
    "The grace period is a prehistoric memory.",
    "Still fumbling with the keys after the lock's been changed.",
    "You've managed to turn a 'when' into a 'never'.",
    "The cliff edge is miles behind us now.",
    "Pack it in. It's expired.",
]

CHIMES = [
    "soundbank%3A%2F%2Fsoundlibrary%2Falarms%2Fair_horns%2Fair_horn_01",
    "soundbank%3A%2F%2Fsoundlibrary%2Falarms%2Fbeeps_and_bloops%2Fboing_01",
    "soundbank%3A%2F%2Fsoundlibrary%2Falarms%2Fbuzzers%2Fbuzzers_01",
    "soundbank%3A%2F%2Fsoundlibrary%2Falarms%2Fbuzzers%2Fbuzzers_04",
    "soundbank%3A%2F%2Fsoundlibrary%2Falarms%2Fchimes_and_bells%2Fchimes_bells_04",
    "soundbank%3A%2F%2Fsoundlibrary%2Fhome%2Famzn_sfx_doorbell_01",
    "soundbank%3A%2F%2Fsoundlibrary%2Fhome%2Famzn_sfx_doorbell_chime_02",
    "soundbank%3A%2F%2Fsoundlibrary%2Fscifi%2Famzn_sfx_scifi_timer_beep_01",
    "soundbank%3A%2F%2Fsoundlibrary%2Fscifi%2Famzn_sfx_scifi_alarm_01",
    "soundbank%3A%2F%2Fsoundlibrary%2Falarms%2Fbeeps_and_bloops%2Fbuzz_03",
    "soundbank%3A%2F%2Fsoundlibrary%2Fmusical%2Famzn_sfx_test_tone_01",
]

def get_db():
    conn = sqlite3.connect('tasks.db')
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            deadline TEXT NOT NULL,
            status TEXT DEFAULT 'active',
            last_alert_type TEXT DEFAULT 'none',
            last_nag_time TEXT,
            percent INTEGER DEFAULT 0,
            phase TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS recurring_templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            start_time TEXT NOT NULL,
            interval TEXT NOT NULL,
            last_generated TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """)
    # Default settings
    c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('briefing_time', '08:00')")
    c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('dnd_start', '22:00')")
    c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('dnd_end', '07:00')")
    c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('nag_interval', '15')")
    c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('port', '5001')")
    
    conn.commit()
    conn.close()


def trigger_voice_monkey(text, device=None, chime=None):
    """Fire a VM announcement. Skips if VM=false in config or DND is active."""
    if not VM_ENABLED or not VM_TOKEN:
        return

    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT key, value FROM settings WHERE key IN ('dnd_start', 'dnd_end', 'silence_mode')")
    sets = {row[0]: row[1] for row in c.fetchall()}
    conn.close()

    if sets.get('silence_mode') == 'on':
        return

    now_time = datetime.now().strftime('%H:%M')
    dnd_start = sets.get('dnd_start', '22:00')
    dnd_end = sets.get('dnd_end', '07:00')
    if dnd_start > dnd_end:
        if now_time >= dnd_start or now_time <= dnd_end:
            return
    else:
        if dnd_start <= now_time <= dnd_end:
            return

    target_device = device or VM_DEVICE_ALERTS
    url = "https://api-v2.voicemonkey.io/announcement"
    params = {
        "token": VM_TOKEN,
        "device": target_device,
        "text": text,
        "voice": random.choice(VOICES),
        "language": VM_LANGUAGE,
    }
    if chime:
        params["chime"] = chime

    try:
        requests.get(url, params=params, timeout=5)
    except:
        pass

def get_setting(key, default=None):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT value FROM settings WHERE key=?", (key,))
    res = c.fetchone()
    conn.close()
    return res[0] if res else default

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    conn = get_db()
    c = conn.cursor()
    
    if request.method == 'POST':
        # List of keys to process normally
        setting_keys = ['briefing_time', 'dnd_start', 'dnd_end', 'bar_start_hours', 'nag_interval', 'port']

        for key in setting_keys:
            val = request.form.get(key)
            if not val:
                return f"Error: Field '{key}' is compulsory.", 400
            c.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, val))
        
        # Handle the Day Buttons: Get the list and join into "Mon,Tue,Wed"
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

def run_morning_briefing():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT key, value FROM settings WHERE key IN ('briefing_time', 'briefing_days')")
    sets = {row[0]: row[1] for row in c.fetchall()}

    now = datetime.now()
    current_time = now.strftime('%H:%M')
    current_day_str = now.strftime('%a')

    if current_time == sets.get('briefing_time') and current_day_str in sets.get('briefing_days', ''):
        c.execute("SELECT title, deadline FROM tasks WHERE status='active' ORDER BY deadline ASC LIMIT 5")
        tasks = c.fetchall()
        conn.close()

        if not tasks:
            return

        quote = random.choice(MORNING_QUOTES)
        message = f"Good morning {USER_NAME}. {quote} Here are your top tasks. "

        for i, task in enumerate(tasks, 1):
            title, deadline_str = task
            dt = datetime.strptime(deadline_str.replace('T', ' '), '%Y-%m-%d %H:%M')
            if dt.date() == now.date():
                day_speak = "today"
            else:
                day_speak = dt.strftime('%A the %d of %B')
            time_speak = dt.strftime('%H:%M')
            if dt < now:
                message += f"Task {i}: {title}, overdue since {day_speak} at {time_speak}. "
            else:
                message += f"Task {i}: {title}, due {day_speak} at {time_speak}. "

        trigger_voice_monkey(message, device=VM_DEVICE_BRIEFINGS)
    else:
        conn.close()

def check_recurring():
    conn = get_db()
    c = conn.cursor()
    
    # Fetch all master templates
    c.execute("SELECT title, start_time, interval FROM recurring_templates")
    templates = c.fetchall()

    for temp in templates:
        title, start_time, interval = temp
        
        # We look for ANY instance of this task in the tasks table
        # If no instance exists at all, we create the first one for 'today' 
        # (or the next logical occurrence)
        c.execute("SELECT deadline FROM tasks WHERE title=? ORDER BY deadline DESC LIMIT 1", (title,))
        last_instance = c.fetchone()
        
        if not last_instance:
            # No instance exists? Create one for today.
            first_deadline = f"{datetime.now().strftime('%Y-%m-%d')}T{start_time}"
            
            # Final safety check: matches title and deadline
            c.execute("SELECT id FROM tasks WHERE title=? AND deadline=?", (title, first_deadline))
            if not c.fetchone():
                c.execute("INSERT INTO tasks (title, deadline, last_alert_type) VALUES (?, ?, 'none')", 
                          (title, first_deadline))
    
    conn.commit()
    conn.close()

def background_task_checker():
    import time
    while True:
        try:
            run_morning_briefing()
            check_recurring()
            
            conn = sqlite3.connect('tasks.db')
            try:
                c = conn.cursor()
                
                c.execute("SELECT value FROM settings WHERE key='silence_mode'")
                res_silence = c.fetchone()
                silence_mode = res_silence[0] if res_silence else 'off'

                c.execute("SELECT value FROM settings WHERE key='nag_interval'")
                res_nag = c.fetchone()
                nag_interval = int(res_nag[0]) if res_nag else 15
                
                if silence_mode == 'off':
                    c.execute("SELECT id, title, deadline, status, last_alert_type, last_nag_time FROM tasks WHERE status='active'")
                    all_tasks = c.fetchall()
                    now = datetime.now()
                    
                    for task in all_tasks:
                        t_id, t_title, t_deadline, t_status, t_last_alert, last_nag_val = task
                        deadline_dt = datetime.strptime(t_deadline.replace('T', ' '), '%Y-%m-%d %H:%M')
                        time_left_mins = (deadline_dt - now).total_seconds() / 60
                        
                    if time_left_mins <= 0:
                        should_nag = False
                        if t_last_alert == 'none' or t_last_alert == 'nag_30' or t_last_alert == 'nag_15':
                            # First time hitting deadline — use NAG_DEADLINE
                            should_nag = True
                            nag_list = NAG_DEADLINE
                            new_alert_type = 'nag_expired'
                        elif t_last_alert == 'nag_expired':
                            if last_nag_val:
                                last_nag_dt = datetime.strptime(last_nag_val, '%Y-%m-%d %H:%M:%S')
                                if (now - last_nag_dt).total_seconds() / 60 >= nag_interval:
                                    should_nag = True
                            else:
                                should_nag = True
                            nag_list = NAG_EXPIRED
                            new_alert_type = 'nag_expired'

                        if should_nag:
                            nag_text = f"{USER_NAME}. {t_title}. {random.choice(nag_list)}"
                            trigger_voice_monkey(nag_text, chime=random.choice(CHIMES))
                            c.execute("UPDATE tasks SET last_alert_type=?, last_nag_time=? WHERE id=?",
                                      (new_alert_type, now.strftime('%Y-%m-%d %H:%M:%S'), t_id))

                    elif 0 < time_left_mins <= 15 and t_last_alert not in ('nag_15', 'nag_expired', 'nag_deadline'):
                        nag_text = f"{USER_NAME}. {t_title}. 15 minutes until deadline. {random.choice(NAG_15)}"
                        trigger_voice_monkey(nag_text, chime=random.choice(CHIMES))
                        c.execute("UPDATE tasks SET last_alert_type='nag_15' WHERE id=?", (t_id,))

                    elif 15 < time_left_mins <= 30 and t_last_alert not in ('nag_30', 'nag_15', 'nag_expired', 'nag_deadline'):
                        nag_text = f"{USER_NAME}. {t_title}. 30 minutes until deadline. {random.choice(NAG_30)}"
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


@app.route('/')
def index():
    # Check for first-run setup
    if not config.get('setup_complete'):
        return redirect('/setup')

    # Detect if the visitor is on a mobile device

    ua = request.headers.get('User-Agent', '').lower()
    is_mobile = any(x in ua for x in ['iphone', 'android', 'mobile'])

    conn = get_db()
    c = conn.cursor()
    
    # 1. Fetch settings
    c.execute("SELECT value FROM settings WHERE key='bar_start_hours'")
    res_bar = c.fetchone()
    bar_scale_hours = float(res_bar[0]) if res_bar else 24.0
    bar_scale_mins = bar_scale_hours * 60

    c.execute("SELECT value FROM settings WHERE key='silence_mode'")
    res_silence = c.fetchone()
    silence_mode = res_silence[0] if res_silence else 'off'

    # 2. Fetch tasks
    c.execute("SELECT id, title, deadline, status FROM tasks WHERE status='active' ORDER BY deadline ASC")
    all_tasks = c.fetchall()
    
    processed_tasks = []
    now = datetime.now()
    
    for task in all_tasks:
        t_id, t_title, t_deadline, t_status = task
        deadline_dt = datetime.strptime(t_deadline.replace('T', ' '), '%Y-%m-%d %H:%M')
        time_left_mins = (deadline_dt - now).total_seconds() / 60
        
        # Visual phase logic
        if time_left_mins <= 0: phase = "phase-red"
        elif time_left_mins <= 15: phase = "phase-orange"
        elif time_left_mins <= 30: phase = "phase-yellow"
        else: phase = "phase-normal"

        percent = max(0, min(100, 100 - (time_left_mins / bar_scale_mins * 100)))
        readable_deadline = deadline_dt.strftime('%a %d %b %H:%M').upper()

        processed_tasks.append({
            'id': t_id, 
            'title': t_title, 
            'deadline': readable_deadline,
            'percent': percent, 
            'phase': phase
        })




    conn.commit()

    # 3. DND Visual Check
    c.execute("SELECT value FROM settings WHERE key='dnd_start'")
    d_start_res = c.fetchone()
    d_start = d_start_res[0] if d_start_res else '22:00'
    
    c.execute("SELECT value FROM settings WHERE key='dnd_end'")
    d_end_res = c.fetchone()
    d_end = d_end_res[0] if d_end_res else '07:00'
    
    now_t = datetime.now().strftime('%H:%M')
    is_dnd = False
    if d_start > d_end:
        if now_t >= d_start or now_t <= d_end: is_dnd = True
    else:
        if d_start <= now_t <= d_end: is_dnd = True

    conn.close()

    return render_template('index.html', 
                           main_tasks=processed_tasks[:5], 
                           queue_tasks=processed_tasks[5:15], 
                           silence_mode=silence_mode,
                           dnd_active=is_dnd,
                           is_mobile=is_mobile) # Pass the flag to the HTML

@app.route('/api/tasks')
def tasks_json():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id, title, deadline, status FROM tasks WHERE status='active' ORDER BY deadline ASC")
    tasks = c.fetchall()
    conn.close()
    
    # Minimal transform to keep it lightweight
    return jsonify([{
        "id": t[0],
        "title": t[1],
        "deadline": t[2],
        "status": t[3]
    } for t in tasks])


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
            
        conn = get_db()
        c = conn.cursor()

        try:
            if task_type == 'recurring':
                interval = request.form.get('interval')
                recur_time = request.form.get('recur_time')
                recur_start_date = request.form.get('recur_start_date')
                
                if not all([interval, recur_time, recur_start_date]):
                    return "Error: All recurring fields are compulsory.", 400
                
                if '-' in recur_start_date:
                    iso_start_date = recur_start_date
                else:
                    day, month, year = recur_start_date.split('/')
                    iso_start_date = f"{year}-{month}-{day}"
                
                now_today = datetime.now().strftime('%Y-%m-%d')

                c.execute("INSERT INTO recurring_templates (title, start_time, interval, last_generated) VALUES (?, ?, ?, ?)",
                          (title, recur_time, interval, now_today))
                first_deadline = f"{iso_start_date}T{recur_time}"
                c.execute("INSERT INTO tasks (title, deadline, last_alert_type) VALUES (?, ?, 'none')", 
                          (title, first_deadline))
            else:
                uk_date = request.form.get('deadline_date')
                d_time = request.form.get('deadline_time')
                
                if not all([uk_date, d_time]):
                    return "Error: All date and time fields are compulsory.", 400
                    
                if '-' in uk_date:
                    iso_date = uk_date
                else:
                    day, month, year = uk_date.split('/')
                    iso_date = f"{year}-{month}-{day}"
                
                deadline = f"{iso_date}T{d_time}"
                c.execute("INSERT INTO tasks (title, deadline, last_alert_type) VALUES (?, ?, 'none')", 
                          (title, deadline))
            
            conn.commit()
            conn.close()
            return redirect('/')
        except Exception as e:
            conn.close()
            return f"Error: {e}. Go back and check your data format.", 400
            
    return render_template('add.html')

@app.route('/complete/<int:task_id>', methods=['POST'])
def complete_task(task_id):
    conn = get_db()
    c = conn.cursor()
    
    # 1. Get the details of the task being completed
    c.execute("SELECT title, deadline FROM tasks WHERE id=?", (task_id,))
    task = c.fetchone()
    
    if task:
        title, current_deadline = task
        # Mark current as done
        c.execute("UPDATE tasks SET status='done' WHERE id=?", (task_id,))
        
        # 2. Check if this task belongs to a recurring template
        c.execute("SELECT interval FROM recurring_templates WHERE title=?", (title,))
        template = c.fetchone()
        
        if template:
            interval = template[0]
            old_dt = datetime.strptime(current_deadline.replace('T', ' '), '%Y-%m-%d %H:%M')
            
            # Calculate next date based on interval
            # Parse new interval format (e.g., "1D", "2W")
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
                import calendar
                new_dt = old_dt
                for _ in range(count):
                    month = new_dt.month % 12 + 1
                    year = new_dt.year + (new_dt.month // 12)
                    day = min(new_dt.day, calendar.monthrange(year, month)[1])
                    new_dt = new_dt.replace(year=year, month=month, day=day)
            
            new_deadline = new_dt.strftime('%Y-%m-%dT%H:%M')


            # 3. DUPLICATE CHECK: Only add if not already in tasks (active OR done)
            c.execute("SELECT id FROM tasks WHERE title=? AND deadline=?", (title, new_deadline))
            if not c.fetchone():
                c.execute("INSERT INTO tasks (title, deadline, last_alert_type) VALUES (?, ?, 'none')", 
                          (title, new_deadline))
        
        conn.commit()
        conn.close()

        # Celebration Data
        msg = random.choice(PRAISE_MESSAGES).format(name=USER_NAME)
        selected_theme = random.choice(['matrix', 'glitch', 'gold-rush', 'fireworks', 'confetti'])
        trigger_voice_monkey(msg)
        
        applause_num = random.randint(1, 8)
        audio_url = f"/soundfx/applause{applause_num}.mp3"

        return jsonify({"status": "success", "message": msg, "theme": selected_theme, "audio": audio_url})
    
    conn.close()
    return jsonify({"status": "error"}), 404

@app.route('/recovery')
def recovery():
    conn = get_db()
    c = conn.cursor()
    # Fetch newest first
    c.execute("SELECT id, title, deadline FROM tasks WHERE status='done' ORDER BY id DESC LIMIT 20")
    rows = c.fetchall()
    

    processed_recovery = []
    for r in rows:
        t_id, title, deadline_str = r
        # UK Format: Weekday, Date, Month, Year, Time
        dt = datetime.strptime(deadline_str.replace('T', ' '), '%Y-%m-%d %H:%M')
        uk_format = dt.strftime('%A, %d %b %Y %H:%M').upper()
        
        processed_recovery.append({
            'id': t_id,
            'title': title,
            'was_due': uk_format
        })
        
    conn.close()
    return render_template('recovery.html', tasks=processed_recovery)

@app.route('/restore/<int:task_id>', methods=['POST'])
def restore_task(task_id):
    conn = get_db()
    c = conn.cursor()
    # Reset status to active and clear the alert type to re-trigger notifications
    c.execute("UPDATE tasks SET status='active', last_alert_type='none', last_nag_time=NULL WHERE id=?", (task_id,))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/manage_recurring')
def manage_recurring():
    conn = get_db()
    c = conn.cursor()
    # Fetch templates
    c.execute("SELECT id, title, start_time, interval FROM recurring_templates")
    rows = c.fetchall()
    
    processed_templates = []
    for r in rows:
        t_id, title, s_time, interval = r
        
        # Look up the first task created for this title to get the original date
        c.execute("SELECT deadline FROM tasks WHERE title=? ORDER BY id ASC LIMIT 1", (title,))
        task_res = c.fetchone()
        
        display_str = ""
        if task_res:
            # Parse the deadline (Format: YYYY-MM-DDTHH:MM)
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
                if 11 <= day_num <= 13: suffix = 'TH'
                else: suffix = {1: 'ST', 2: 'ND', 3: 'RD'}.get(day_num % 10, 'TH')
                display_str = f"EVERY {count} MONTHS (ON THE {day_num}{suffix}) @ {s_time}" if count > 1 else f"EVERY {day_num}{suffix} OF THE MONTH @ {s_time}"
            
            processed_templates.append({

            'id': t_id,
            'title': title,
            'display': display_str
        })
        
    conn.close()
    return render_template('manage_recurring.html', templates=processed_templates)

@app.route('/delete_template/<int:t_id>', methods=['POST'])
def delete_template(t_id):
    conn = get_db()
    c = conn.cursor()
    # 1. Delete the template from the recurring table
    c.execute("DELETE FROM recurring_templates WHERE id=?", (t_id,))
    conn.commit()
    conn.close()
    # 2. Bounce back to the list so you can delete the next one
    return redirect('/manage_recurring')

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
        if choice == 'no':
            config['setup_complete'] = True
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=4)
            return redirect('/')
        else:
            return redirect('/setup_oauth')
    return render_template('setup_backup.html')

@app.route('/setup_oauth', methods=['GET', 'POST'])
def setup_oauth():
    if request.method == 'POST':
        client_id = request.form.get('client_id')
        client_secret = request.form.get('client_secret')
        
        if not all([client_id, client_secret]):
            return "Error: All fields are compulsory.", 400
            
        # Save credentials here (mocking for now or saving to config)
        config['setup_complete'] = True
        config['gdrive_client_id'] = client_id
        config['gdrive_client_secret'] = client_secret
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)
        return redirect('/')
    return render_template('setup_oauth.html')


@app.route('/edit_list')
def edit_list():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id, title, deadline FROM tasks WHERE status='active' ORDER BY deadline ASC")
    tasks = c.fetchall()
    conn.close()
    
    # Process deadlines for readable format
    processed = []
    for t in tasks:
        processed.append({
            'id': t[0],
            'title': t[1],
            'deadline': t[2]
        })
    return render_template('edit_list.html', tasks=processed)

@app.route('/edit/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    conn = get_db()
    c = conn.cursor()
    
    if request.method == 'POST':
        uk_date = request.form.get('deadline_date')
        d_time = request.form.get('deadline_time')
        
        if not all([uk_date, d_time]):
            return "Error: All fields are compulsory.", 400
            
        if '-' in uk_date:
            iso_date = uk_date
        else:
            day, month, year = uk_date.split('/')
            iso_date = f"{year}-{month}-{day}"
            
        deadline = f"{iso_date}T{d_time}"
        
        c.execute("UPDATE tasks SET deadline=?, last_alert_type='none', last_nag_time=NULL WHERE id=?", (deadline, task_id))
        conn.commit()
        conn.close()
        return redirect('/')
        
    c.execute("SELECT id, title, deadline FROM tasks WHERE id=?", (task_id,))
    task = c.fetchone()
    conn.close()
    
    if not task:
        return "Task not found", 404
        
    # Split deadline for the view
    dt_str = task[2].replace('T', ' ')
    from datetime import datetime
    dt = datetime.strptime(dt_str, '%Y-%m-%d %H:%M')
    
    return render_template('edit_task.html', task={
        'id': task[0],
        'title': task[1],
        'date': dt.strftime('%d/%m/%Y'),
        'time': dt.strftime('%H:%M')
    })


if __name__ == '__main__':
    init_db()

    # Get port from DB
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    c.execute("SELECT value FROM settings WHERE key='port'")
    res = c.fetchone()
    app_port = int(res[0]) if res else 5001
    conn.close()

    import threading
    t = threading.Thread(target=background_task_checker, daemon=True)
    t.start()
    
    import logging
    logging.getLogger('werkzeug').setLevel(logging.ERROR)
    
    app.run(host='0.0.0.0', port=app_port, debug=True)


