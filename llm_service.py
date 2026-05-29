import json
import os
import sqlite3
import requests
from datetime import datetime

_CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.json')
_DB_PATH = os.path.join(os.path.dirname(__file__), 'tasks.db')


def _get_cfg():
    cfg = {}
    # Try config.json first
    try:
        with open(_CONFIG_PATH) as f:
            c = json.load(f)
        cfg = {
            'provider': c.get('llm_provider', '').lower(),
            'quick_model': c.get('llm_quick_model', ''),
            'deep_model': c.get('llm_deep_model', ''),
            'api_key': c.get('llm_api_key', ''),
            'ollama_host': c.get('llm_ollama_host', 'http://localhost:11434'),
        }
    except Exception:
        pass

    # Overlay with DB settings (DB takes precedence — configured via UI)
    try:
        conn = sqlite3.connect(_DB_PATH)
        c = conn.cursor()
        c.execute(
            "SELECT key, value FROM settings WHERE key IN "
            "('llm_provider','llm_quick_model','llm_deep_model','llm_api_key','llm_ollama_host')"
        )
        rows = {row[0]: row[1] for row in c.fetchall()}
        conn.close()
        if rows.get('llm_provider'):
            cfg['provider'] = rows['llm_provider'].lower()
        if rows.get('llm_quick_model'):
            cfg['quick_model'] = rows['llm_quick_model']
        if rows.get('llm_deep_model'):
            cfg['deep_model'] = rows['llm_deep_model']
        if rows.get('llm_api_key'):
            cfg['api_key'] = rows['llm_api_key']
        if rows.get('llm_ollama_host'):
            cfg['ollama_host'] = rows['llm_ollama_host']
    except Exception:
        pass

    return cfg


def call_llm(prompt, model_type='quick', system_prompt=None):
    cfg = _get_cfg()
    provider = cfg.get('provider', '')
    model = cfg.get('quick_model') if model_type == 'quick' else cfg.get('deep_model')
    api_key = cfg.get('api_key', '')

    if not provider or not model:
        return None

    try:
        if provider == 'openai':
            msgs = []
            if system_prompt:
                msgs.append({'role': 'system', 'content': system_prompt})
            msgs.append({'role': 'user', 'content': prompt})
            r = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers={'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'},
                json={'model': model, 'messages': msgs, 'max_tokens': 600},
                timeout=20
            )
            r.raise_for_status()
            return r.json()['choices'][0]['message']['content'].strip()

        elif provider == 'anthropic':
            payload = {
                'model': model,
                'max_tokens': 600,
                'messages': [{'role': 'user', 'content': prompt}]
            }
            if system_prompt:
                payload['system'] = system_prompt
            r = requests.post(
                'https://api.anthropic.com/v1/messages',
                headers={
                    'x-api-key': api_key,
                    'anthropic-version': '2023-06-01',
                    'Content-Type': 'application/json'
                },
                json=payload,
                timeout=20
            )
            r.raise_for_status()
            return r.json()['content'][0]['text'].strip()

        elif provider == 'ollama':
            msgs = []
            if system_prompt:
                msgs.append({'role': 'system', 'content': system_prompt})
            msgs.append({'role': 'user', 'content': prompt})
            r = requests.post(
                f"{cfg['ollama_host']}/api/chat",
                json={'model': model, 'messages': msgs, 'stream': False},
                timeout=60
            )
            r.raise_for_status()
            return r.json()['message']['content'].strip()

    except Exception as e:
        print(f"LLM call failed ({provider}/{model}): {e}")
        return None


def _clean_json(raw):
    if not raw:
        return None
    s = raw.strip().strip('`').strip()
    if s.startswith('json'):
        s = s[4:].strip()
    return s


def test_connection():
    result = call_llm("Reply with the single word OK.", model_type='quick')
    if result and 'ok' in result.lower():
        return True, "Connection successful."
    return False, "Connection failed — check provider, model name, and API key in settings."


def estimate_duration(task_title, buffer_pct=30):
    sys_p = (
        'You are an ADHD task management assistant. Estimate realistic task durations. '
        'Respond with JSON ONLY: {"minutes": <integer>, "rationale": "<one sentence>"}'
    )
    result = call_llm(f'Estimate minutes for: "{task_title}"', 'quick', sys_p)
    if not result:
        return None
    try:
        data = json.loads(_clean_json(result))
        raw = int(data['minutes'])
        buf = max(5, round(raw * (1 + buffer_pct / 100) / 5) * 5)
        return raw, buf, data.get('rationale', '')
    except Exception:
        return None


def get_first_step(task_title):
    sys_p = (
        'Give ONE concrete first physical action in 10 words or fewer. '
        'No motivation or preamble — just the physical action to take right now.'
    )
    result = call_llm(f'Task: "{task_title}"', 'quick', sys_p)
    return result.strip('"').strip() if result else 'Take the first small step right now.'


def generate_message_bank():
    nag_sys = (
        'Generate exactly 25 short, snarky British nag messages for overdue tasks. '
        'Each under 12 words. Brutal, cutting wit, no task names, no names. '
        'Return a JSON array of 25 strings ONLY. No other text.'
    )
    praise_sys = (
        'Generate exactly 25 short, warm celebration messages for completed tasks. '
        'Each under 12 words. Genuinely enthusiastic and warm. No task names, no names. '
        'Return a JSON array of 25 strings ONLY. No other text.'
    )
    messages = []
    for sys_p, mtype in [(nag_sys, 'nag'), (praise_sys, 'praise')]:
        result = call_llm('Generate the messages now.', 'quick', sys_p)
        if result:
            try:
                items = json.loads(_clean_json(result))
                messages.extend({'type': mtype, 'text': str(t)} for t in items[:25])
            except Exception as e:
                print(f"Message bank parse error ({mtype}): {e}")
    return messages


def parse_natural_language_task(text):
    today = datetime.now().strftime('%Y-%m-%d')
    sys_p = (
        f'Today is {today}. Parse a task description and return ONLY JSON with these fields: '
        '"title" (clean task title string), '
        '"deadline_date" (YYYY-MM-DD or empty string), '
        '"deadline_time" (HH:MM or "09:00" if date given but no time), '
        '"deadline_type" ("fixed" for hard deadlines, "flexible" for casual dates, "none" for no date), '
        '"duration_minutes" (integer estimate or 0 if not mentioned). '
        'Return JSON ONLY.'
    )
    result = call_llm(text, 'quick', sys_p)
    if not result:
        return None
    try:
        return json.loads(_clean_json(result))
    except Exception:
        return None


def rebalance_suggestion(day_name, week_tasks, daily_capacity):
    sys_p = (
        'You are an ADHD scheduling assistant. Suggest ONE task to move from an overloaded day. '
        'Never move fixed-deadline tasks. Prefer no-deadline first, then flexible. '
        'Return ONLY JSON: {"task_id": <int>, "task_title": "<str>", "move_to": "<day abbrev e.g. Tue>", "reason": "<one sentence>"}'
    )
    context = f"Overloaded day: {day_name}\n\nFull week schedule:\n"
    for day, tasks in week_tasks.items():
        cap = daily_capacity.get(day, 6.0)
        total_h = sum(t.get('duration_minutes', 30) for t in tasks) / 60
        context += f"\n{day} ({total_h:.1f}h planned / {cap}h available):\n"
        for t in tasks:
            context += (
                f"  [{t['id']}] {t['title']} "
                f"({t.get('duration_minutes', 30)}min, {t.get('deadline_type', 'flexible')})\n"
            )
    result = call_llm(context, 'deep', sys_p)
    if not result:
        return None
    try:
        return json.loads(_clean_json(result))
    except Exception:
        return None


def breakdown_complex_task(task_title, deadline, answers):
    today = datetime.now().strftime('%Y-%m-%d')
    sys_p = (
        'You are an ADHD task breakdown specialist. Break the task into 3-7 concrete subtasks. '
        'Sequence them correctly. Each 15-120 minutes. Spread over available days before deadline. '
        'Return ONLY a JSON array: '
        '[{"title":"...", "duration_minutes":<int>, "deadline_date":"YYYY-MM-DD", "deadline_time":"HH:MM"}]'
    )
    prompt = (
        f'Today: {today}. Task: "{task_title}". '
        f'Final deadline: {deadline}. '
        f'User context: {json.dumps(answers)}'
    )
    result = call_llm(prompt, 'deep', sys_p)
    if not result:
        return []
    try:
        return json.loads(_clean_json(result))
    except Exception:
        return []
