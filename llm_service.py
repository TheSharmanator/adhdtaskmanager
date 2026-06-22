import os
import sqlite3
import requests
from datetime import datetime

_DB_PATH = os.path.join(os.path.dirname(__file__), 'tasks.db')

_last_error = ''


def _get_cfg():
    cfg = {}
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


def call_llm(prompt, model_type='quick', system_prompt=None, overrides=None):
    global _last_error
    _last_error = ''
    cfg = _get_cfg()
    # Live overrides (e.g. from the settings form Test button) take top precedence
    if overrides:
        if overrides.get('provider'):
            cfg['provider'] = overrides['provider'].lower()
        if overrides.get('quick_model'):
            cfg['quick_model'] = overrides['quick_model'].strip()
        if overrides.get('deep_model'):
            cfg['deep_model'] = overrides['deep_model'].strip()
        if overrides.get('api_key'):
            cfg['api_key'] = overrides['api_key'].strip()
        if overrides.get('ollama_host'):
            cfg['ollama_host'] = overrides['ollama_host'].strip()

    provider = cfg.get('provider', '')
    model = cfg.get('quick_model') if model_type == 'quick' else cfg.get('deep_model')
    api_key = cfg.get('api_key', '').strip()

    # Local providers can run without an explicit model name (server picks the loaded model)
    if provider in ('llamacpp', 'ollama') and not model:
        model = 'local'

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

        elif provider == 'google':
            payload = {'contents': [{'role': 'user', 'parts': [{'text': prompt}]}]}
            if system_prompt:
                payload['system_instruction'] = {'parts': [{'text': system_prompt}]}
            r = requests.post(
                f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}',
                headers={'Content-Type': 'application/json'},
                json=payload,
                timeout=20
            )
            r.raise_for_status()
            return r.json()['candidates'][0]['content']['parts'][0]['text'].strip()

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

        elif provider == 'llamacpp':
            msgs = []
            if system_prompt:
                msgs.append({'role': 'system', 'content': system_prompt})
            msgs.append({'role': 'user', 'content': prompt})
            host = cfg.get('ollama_host', 'http://localhost:8080')
            r = requests.post(
                f"{host}/v1/chat/completions",
                json={'model': model or 'local', 'messages': msgs, 'max_tokens': 600},
                timeout=60
            )
            r.raise_for_status()
            return r.json()['choices'][0]['message']['content'].strip()

    except requests.exceptions.HTTPError as e:
        # Extract the real error message from the API response body
        err_detail = str(e)
        try:
            body = e.response.json()
            err_obj = body.get('error') or body
            if isinstance(err_obj, dict):
                err_detail = err_obj.get('message') or err_obj.get('type') or err_detail
            # HTTP status for context
            err_detail = f"HTTP {e.response.status_code}: {err_detail}"
        except Exception:
            pass
        _last_error = err_detail
        print(f"LLM call failed ({provider}/{model}): {err_detail}")
        return None
    except requests.exceptions.ConnectionError:
        _last_error = f"Cannot reach {provider} — check host/network connection."
        print(f"LLM call failed ({provider}/{model}): {_last_error}")
        return None
    except Exception as e:
        _last_error = str(e)
        print(f"LLM call failed ({provider}/{model}): {e}")
        return None


def _clean_json(raw):
    if not raw:
        return None
    s = raw.strip().strip('`').strip()
    if s.startswith('json'):
        s = s[4:].strip()
    return s


def test_connection(overrides=None):
    result = call_llm("Reply with the single word OK.", model_type='quick', overrides=overrides)
    if result and 'ok' in result.lower():
        return True, "Connection successful."
    if result:
        return True, "Connection successful (model replied)."
    if _last_error:
        return False, _last_error
    return False, "No response — check provider and model name."


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
    nudge_sys = (
        'Generate exactly 25 short, punchy focus reminders for someone with ADHD working in focus mode. '
        'Each under 12 words. Address common ADHD focus failures: task-switching, shiny-object syndrome, '
        'side quests, phone checking, time blindness, opening new tabs, rabbit holes, losing momentum. '
        'Tone: direct, no-nonsense, encouraging not shaming. No names. '
        'Return a JSON array of 25 strings ONLY. No other text.'
    )
    messages = []
    for sys_p, mtype in [(nag_sys, 'nag'), (praise_sys, 'praise'), (nudge_sys, 'focus_nudge')]:
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


def generate_breakdown_questions(task_title):
    """Return 5 task-specific questions each with 2-4 answer options, or None on failure."""
    sys_p = (
        'You are an ADHD task-planning assistant. '
        'Given a task title, generate exactly 5 questions that clarify the scope, '
        'dependencies, and approach for THAT SPECIFIC task. '
        'Each question must have 2-4 short answer options that are genuinely distinct '
        'and useful for planning — not just "Yes" and "No" unless that is truly the right shape. '
        'Questions and options must be specific to the task, not generic. '
        'Return ONLY a JSON array of 5 objects, no explanation: '
        '[{"question": "...", "options": ["option A", "option B", ...]}, ...]'
    )
    prompt = f'Task: "{task_title}"\nGenerate 5 planning questions with specific answer options.'
    result = call_llm(prompt, 'quick', sys_p)
    if not result:
        return None
    try:
        questions = json.loads(_clean_json(result))
        if isinstance(questions, list) and len(questions) >= 3:
            validated = []
            for q in questions[:5]:
                if isinstance(q, dict) and q.get('question') and isinstance(q.get('options'), list) and len(q['options']) >= 2:
                    validated.append({'question': str(q['question']), 'options': [str(o) for o in q['options'][:4]]})
            if len(validated) >= 3:
                return validated
    except Exception:
        pass
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
