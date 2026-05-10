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
    VM_TOKEN = config.get('VM_TOKEN')
    VM_DEVICE = config.get('VM_DEVICE')
    VM_MORNING_DEVICE = config.get('VM_MORNING_DEVICE')




MORNING_GREETINGS = [
    "Good morning, Joe. Success is the sum of small efforts repeated daily. Your top tasks are...",
    "Morning, mate. Focus on being productive instead of busy. Here’s the plan...",
    "Wake up, Joe. Your future self is counting on you today. You've got these tasks...",
    "Good morning. Discipline is doing what needs to be done even if you don't feel like it. Top 5...",
    "Morning, Sharmanator. Don't stop until you're proud. Starting with...",
    "Good morning, Joe. Today is another chance to get it right. Your priority list is...",
    "Morning! Great things never come from comfort zones. Let's tackle these...",
    "Wake up and win, Joe. Action is the foundational key to all success. Your top 5...",
    "Good morning. The only way to do great work is to love what you do. Let's start with...",
    "Morning, Joe. Your focus determines your reality. Here is your focus for today...",
    "Good morning. Make today count. You’ll never get this day back. First up...",
    "Morning, mate. Small wins lead to big victories. Let’s get these out of the way...",
    "Good morning, Joe. Excellence is not an act, but a habit. Your habits for today are...",
    "Morning! Don't count the days, make the days count. Here's your list...",
    "Good morning. Energy and persistence conquer all things. Let's go...",
    "Morning, Joe. Be stronger than your excuses. Your top 5 priorities...",
    "Good morning. Success doesn't just find you. You have to go out and get it. Starting with...",
    "Morning, Sharmanator. The secret of getting ahead is getting started. First tasks...",
    "Good morning, Joe. Hustle until your haters ask if you're hiring. Your board shows...",
    "Morning! Life is short. Don't waste it on things that don't matter. Focus on...",
    "Good morning, Joe. You are capable of amazing things. Let's prove it with...",
    "Morning, mate. Every morning is a new arrival. A new chance. Your top 5...",
    "Good morning. Don't be busy, be productive. Here is what needs doing...",
    "Morning, Joe. Do something today that your future self will thank you for. Like...",
    "Good morning. You didn't wake up today to be mediocre. Let's be legendary. Starting with..."
]

VOICES = ["Nicole", "Russell", "Amy", "Emma", "Brian"]

CHIMES = [
    "soundbank://soundlibrary/alarms/beeps_and_bloops/boing_01",
    "soundbank://soundlibrary/alarms/air_horns/air_horn_01",
    "soundbank://soundlibrary/alarms/beeps_and_bloops/woosh_02",
    "soundbank://soundlibrary/alarms/beeps_and_bloops/bell_01",
    "soundbank://soundlibrary/alarms/beeps_and_bloops/bell_02",
    "soundbank://soundlibrary/alarms/chimes_and_bells/chimes_bells_05",
    "soundbank://soundlibrary/alarms/buzzers/buzzers_01",
    "soundbank://soundlibrary/alarms/chimes_and_bells/chimes_bells_04",
    "soundbank://soundlibrary/alarms/beeps_and_bloops/bell_03",
    "soundbank://soundlibrary/alarms/beeps_and_bloops/bell_04",
    "soundbank://soundlibrary/home/amzn_sfx_doorbell_01",
    "soundbank://soundlibrary/home/amzn_sfx_doorbell_chime_02",
    "soundbank://soundlibrary/musical/amzn_sfx_electronic_beep_01",
    "soundbank://soundlibrary/musical/amzn_sfx_electronic_beep_02",
    "soundbank://soundlibrary/scifi/amzn_sfx_scifi_timer_beep_01",
    "soundbank://soundlibrary/alarms/beeps_and_bloops/intro_02",
    "soundbank://soundlibrary/scifi/amzn_sfx_scifi_alarm_01",
    "soundbank://soundlibrary/alarms/beeps_and_bloops/buzz_03",
    "soundbank://soundlibrary/musical/amzn_sfx_test_tone_01",
    "soundbank://soundlibrary/alarms/beeps_and_bloops/tone_02",
    "soundbank://soundlibrary/alarms/beeps_and_bloops/tone_05",
    "soundbank://soundlibrary/alarms/beeps_and_bloops/woosh_02"
]

APPLAUSES = [f"https://media.voicemonkey.io/vom/u/bd587122d47d74b4e29a0b363b5cb73e/69eb5d0b7ec97/applause{i}.mp3" for i in range(1, 9)]

PRAISE_MESSAGES = [
    "Jolly good show!", "About bloody time.", "Absolute legend.", "Task slain. Who's next?", 
    "Look at you, being a functioning adult.", "Crushed it. Go grab a beer.", "Finally. I was starting to worry.",
    "Superior work, captain.", "You're on fire today!", "Dopamine hit incoming!", 
    "One step closer to freedom.", "Magnificent effort.", "You actually did it. I'm impressed.", 
    "Victory is yours!", "Task demolished. Stay in the zone.", "Efficiency levels are peaking.",
    "That's how it's done.", "Boom. Done. What's next?", "System satisfied. Keep going.", 
    "You're making this look easy.", "Look at that momentum!", "Another one bites the dust.", 
    "Task purged. Feeling lighter?", "You're outperforming your yesterday self.", 
    "A masterful execution.", "Pure productivity.", "The board is pleased.", "Legendary status achieved.",
    "No more nagging for that one!", "Clean sweep.", "You're winning at life right now.",
    "Keep that streak alive.", "Solid work. Don't stop now.", "Task complete. Dopamine delivered.",
    "You're a task-finishing machine.", "Outstanding. Simply outstanding.", "Phenomenal hustle.",
    "Consider that task dominated.", "You've got this handled.", "Smooth operations only.",
    "That's a win in my book.", "Process complete. Well played.", "You're in the flow now.",
    "Top tier productivity.", "Exactly as planned. Well done.", "The queue is shrinking!",
    "Bravo! Truly bravo.", "Focus pays off.", "You're unstoppable today.", "Task buried."
]

NAG_30 = [
    "Heads up! {task} is due in 30 minutes.", "30 minute warning for {task}. Let's get moving.",
    "Clock is ticking, {task} is due in half an hour.", "Don't get distracted! {task} in 30 minutes.",
    "Focus time. {task} is coming up in 30 minutes.", "Interval check: {task} is due in 30.",
    "Just a nudge, {task} is due in 30 minutes.", "Stay on track! {task} is due shortly.",
    "Time blindness check! 30 minutes left for {task}.", "Half hour remaining for {task}."
]

NAG_15 = [
    "Urgent! {task} is due in 15 minutes!", "Double time! 15 minutes left for {task}.",
    "15 minute alert for {task}. Finish strong!", "Final stretch! {task} in 15 minutes.",
    "Don't stop now, {task} is due in 15.", "Crunch time. 15 minutes for {task}.",
    "Incoming deadline! {task} in 15 minutes.", "Alert! Only 15 minutes left for {task}.",
    "Focus, Sharmanator! {task} is due in 15.", "The 15 minute countdown for {task} has started."
]

NAG_EXPIRED = [
    "The deadline for {task} has expired. Do it now.", "Attention! {task} is overdue.",
    "You missed the mark on {task}. Clear it immediately.", "Overdue alert: {task} needs doing.",
    "Stop wasting time. {task} was due already.", "{task} is sitting in the red. Fix it.",
    "Still haven't done {task}? Get it done.", "The board is red! {task} is overdue.",
    "Persistence check: {task} is late. Do it.", "No more excuses, {task} is past due."
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
    
    conn.commit()
    conn.close()


def trigger_voice_monkey(text, chime=None, audio=None):
    # 0. Skip if not fully configured
    if not VM_TOKEN or not VM_DEVICE or not VM_MORNING_DEVICE:
        return

    # 1. Check DND status before doing anything

    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT key, value FROM settings WHERE key IN ('dnd_start', 'dnd_end', 'silence_mode')")
    rows = c.fetchall()
    sets = {row[0]: row[1] for row in rows}
    conn.close()

    # Manual silence check
    if sets.get('silence_mode') == 'on':
        return

    # Time-based DND check
    now_time = datetime.now().strftime('%H:%M')
    start = sets.get('dnd_start', '22:00')
    end = sets.get('dnd_end', '07:00')

    # Handle DND wrapping over midnight (e.g., 22:00 to 07:00)
    if start > end:
        if now_time >= start or now_time <= end:
            return
    else:
        if start <= now_time <= end:
            return

    # 2. If we passed the filters, proceed to trigger
    url = "https://api-v2.voicemonkey.io/announcement"
    params = {
        "token": VM_TOKEN,
        "device": VM_DEVICE,
        "text": text,
        "voice": random.choice(VOICES),
        "language": "en-GB"
    }
    if chime: params["chime"] = chime
    if audio and config.get('VM_USE_SOUND', False): params["audio"] = audio

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
        setting_keys = ['briefing_time', 'dnd_start', 'dnd_end', 'bar_start_hours', 'nag_interval', 'kiosk_mode']

        for key in setting_keys:
            val = request.form.get(key)
            if val:
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
    
    # 1. Fetch briefing settings
    c.execute("SELECT key, value FROM settings WHERE key IN ('briefing_time', 'briefing_days')")
    sets = {row[0]: row[1] for row in c.fetchall()}
    
    now = datetime.now()
    current_time = now.strftime('%H:%M')
    current_day_str = now.strftime('%a') 

    # 2. Time and Day Check
    if current_time == sets.get('briefing_time') and current_day_str in sets.get('briefing_days', ''):
        c.execute("SELECT title, deadline FROM tasks WHERE status='active' ORDER BY deadline ASC LIMIT 5")
        tasks = c.fetchall()
        conn.close()

        if not tasks:
            return

        # 3. Assemble Message with Overdue Awareness
        message = random.choice(MORNING_GREETINGS)
        
        for i, task in enumerate(tasks, 1):
            title, deadline_str = task
            dt = datetime.strptime(deadline_str.replace('T', ' '), '%Y-%m-%d %H:%M')
            
            # Format the date/time string
            if dt.date() == now.date():
                day_speak = "today"
            else:
                day_speak = dt.strftime('%A, the %d of %B')
            
            time_speak = dt.strftime('%H:%M')

            # 4. Phrasing based on Overdue status
            if dt < now:
                message += f" Task {i}: {title} is still overdue. It should've been done on {day_speak} at {time_speak}."
            else:
                message += f" Task {i}: {title}, due {day_speak} at {time_speak}."

        # 5. Trigger Bedroom Alexa
        url = "https://api-v2.voicemonkey.io/announcement"
        params = {
            "token": VM_TOKEN,
            "device": VM_MORNING_DEVICE,
            "text": message,
            "voice": random.choice(VOICES),
            "language": "en-GB"
        }
        try:
            requests.get(url, params=params, timeout=5)
        except:
            pass
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
                        if t_last_alert != 'nag_expired':
                            should_nag = True
                        elif last_nag_val:
                            last_nag_dt = datetime.strptime(last_nag_val, '%Y-%m-%d %H:%M:%S')
                            if (now - last_nag_dt).total_seconds() / 60 >= nag_interval:
                                should_nag = True
                        
                        if should_nag:
                            trigger_voice_monkey(random.choice(NAG_EXPIRED).format(task=t_title), chime=random.choice(CHIMES))
                            c.execute("UPDATE tasks SET last_alert_type='nag_expired', last_nag_time=? WHERE id=?", 
                                      (now.strftime('%Y-%m-%d %H:%M:%S'), t_id))
                    
                    elif 0 < time_left_mins <= 15 and t_last_alert != 'nag_15':
                        trigger_voice_monkey(random.choice(NAG_15).format(task=t_title), chime=random.choice(CHIMES))
                        c.execute("UPDATE tasks SET last_alert_type='nag_15' WHERE id=?", (t_id,))
                    elif 15 < time_left_mins <= 30 and t_last_alert != 'nag_30':
                        trigger_voice_monkey(random.choice(NAG_30).format(task=t_title), chime=random.choice(CHIMES))
                        c.execute("UPDATE tasks SET last_alert_type='nag_30' WHERE id=?", (t_id,))
                
                conn.commit()
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
        title = request.form['title']
        conn = get_db()
        c = conn.cursor()

        try:
            if task_type == 'recurring':
                interval = request.form.get('interval')
                recur_time = request.form.get('recur_time')
                if '-' in uk_start_date:
                    iso_start_date = uk_start_date
                else:
                    day, month, year = uk_start_date.split('/')
                    iso_start_date = f"{year}-{month}-{day}"
                
                now_today = datetime.now().strftime('%Y-%m-%d')

                c.execute("INSERT INTO recurring_templates (title, start_time, interval, last_generated) VALUES (?, ?, ?, ?)",
                          (title, recur_time, interval, now_today))
                first_deadline = f"{iso_start_date}T{recur_time}"
                c.execute("INSERT INTO tasks (title, deadline, last_alert_type) VALUES (?, ?, 'none')", 
                          (title, first_deadline))
            else:
                uk_date = request.form.get('deadline_date')
                if '-' in uk_date:
                    iso_date = uk_date
                else:
                    day, month, year = uk_date.split('/')
                    iso_date = f"{year}-{month}-{day}"
                
                d_time = request.form.get('deadline_time')

                deadline = f"{iso_date}T{d_time}"
                c.execute("INSERT INTO tasks (title, deadline, last_alert_type) VALUES (?, ?, 'none')", 
                          (title, deadline))
            
            conn.commit()
            conn.close()
            return redirect('/')
        except Exception as e:
            conn.close()
            # If it fails, we return the same template with an error so your typed data stays there
            return f"Error: {e}. Go back and check your date format (DD/MM/YYYY)."
            
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
        msg = random.choice(PRAISE_MESSAGES)
        selected_theme = random.choice(['matrix', 'glitch', 'gold-rush', 'fireworks', 'confetti'])
        trigger_voice_monkey(msg, audio=random.choice(APPLAUSES))

        return jsonify({"status": "success", "message": msg, "theme": selected_theme})
    
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


@app.route('/setup', methods=['GET', 'POST'])
def setup():
    if request.method == 'POST':
        choice = request.form.get('backup_choice')
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
        # Save credentials here (mocking for now or saving to config)
        config['setup_complete'] = True
        config['gdrive_client_id'] = request.form.get('client_id')
        config['gdrive_client_secret'] = request.form.get('client_secret')
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



    import threading
    t = threading.Thread(target=background_task_checker, daemon=True)
    t.start()
    app.run(host='0.0.0.0', port=5000, debug=True)

