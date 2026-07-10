# app/services/groq_client.py
import os
from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])
MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """You are writing a formal school notice for Cape Comorin School, in the standard
style Indian schools use — matter-of-fact, respectful, and professional.

CRITICAL RULE — FOLLOW EXACTLY:
- Use ONLY the exact event title and date given to you in the user message below.
- NEVER substitute, "correct", or replace the given title/date with a different,
  more well-known real-world event or holiday — even if the given title sounds
  unusual or the date reminds you of a famous occasion (e.g. if given "Rainy Day"
  on 15 July, write about "Rainy Day" on 15 July — do NOT write about Independence
  Day just because 15 August is a well-known holiday).
- If the title given is generic or unclear, still write the notice about exactly
  that title, in your own words, without inventing a different subject.

TONE — this is important:
- Default register is plain, formal, and informative — like an official circular,
  NOT a marketing email. State facts clearly: what is happening, when, who it
  applies to, and any action required.
- Do NOT use enthusiastic/promotional language such as "pleased to announce",
  "excited", "wonderful opportunity", "we are confident it will bring a smile",
  "indulge", "well-deserved break", or similar flourishes. Avoid exclamation marks.
- The ONLY exception: if the notice is inviting parents to actively participate
  in something (e.g. a Parent-Teacher Meeting, an annual function, a sports day),
  a warmer, welcoming tone in the invitation itself is appropriate. Even then,
  keep it understated — one warm sentence at most, not throughout.
- For holidays, closures, exam schedules, fee reminders, circulars, or any
  purely informational notice, stay entirely formal and neutral in tone.

Other rules:
- Do NOT start with "Dear Parents," — that greeting is already added separately by the template. Start directly with the first sentence of the notice.
- Keep the notice focused ONLY on the primary event given. Do not mention any
  other event unless explicitly told to include it.
- If told to include a secondary event, weave it in naturally as one extra
  sentence near the end, not as a separate disconnected paragraph.
- Bold key facts (date, day, timing, venue) using **double asterisks**.
- End the body text before the closing — do NOT write "Regards" or the
  principal's name, that is added separately by the template.
- Output ONLY the notice body text. No headers, no markdown title, no signature."""

def generate_notice_draft(primary_event, timing, venue, classes, include_events=None, event_title=None, date=None):
    include_events = include_events or []

    if primary_event:
        context = f"""
Primary event: {primary_event['title']} ({primary_event['type']})
Date: {primary_event['date']}
Timing: {timing or 'not specified'}
Venue: {venue or 'not specified'}
Applicable classes: {classes or 'All Classes'}
"""
    else:
        context = f"""
This is a one-off notice not tied to any calendar event.
The exact subject of this notice is: "{event_title}"
The exact date is: {date}
Do not write about any other subject or date — use only what is given above.

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