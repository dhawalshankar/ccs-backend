# app/services/groq_client.py
import os
from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])
MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """You are writing a formal but warm school notice for Cape Comorin School.
Rules:
- Do NOT start with "Dear Parents," — that greeting is already added separately by the template. Start directly with the first sentence of the notice.
- Tone: warm, respectful, appealing to guardians — never cold or robotic.
- Keep the notice focused ONLY on the primary event given. Do not mention any
  other event unless explicitly told to include it.
- If told to include a secondary event, weave it in naturally as one extra
  sentence near the end, not as a separate disconnected paragraph.
- Bold key facts (date, day, timing, venue) using **double asterisks**.
- End the body text before the closing — do NOT write "Regards" or the
  principal's name, that is added separately by the template.
- Output ONLY the notice body text. No headers, no markdown title, no signature."""

def generate_notice_draft(primary_event, timing, venue, classes, include_events=None):
    include_events = include_events or []

    context = f"""
Primary event: {primary_event['title']} ({primary_event['type']})
Date: {primary_event['date']}
Timing: {timing or 'not specified'}
Venue: {venue or 'not specified'}
Applicable classes: {classes or 'All Classes'}
"""
    if include_events:
        context += "\nAlso include a brief mention of these nearby events:\n"
        for ev in include_events:
            context += f"- {ev['title']} on {ev['date']}\n"

    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": context},
        ],
        temperature=0.6,
        max_tokens=500,
    )
    return resp.choices[0].message.content.strip()