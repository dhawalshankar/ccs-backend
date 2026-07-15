import os
import re
import json
import logging
from groq import Groq

logger = logging.getLogger(__name__)

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
- The structured fields you're given are a normalized summary. The user's
  original request text, when provided below, is the ultimate source of truth —
  it may contain nuance, exceptions, or instructions the summary dropped or
  paraphrased. If the two ever conflict, follow the original request.
- If the original request lists multiple concrete instructions or a set of items
  to verify/correct/collect (e.g. fee amount and deadline, or a list of fields
  like name, DOB, father's name, address, phone number), include every one of
  them. Do not drop, merge, or summarize away specific items — each one belongs
  in the notice.

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

FORMATTING for lists of items (e.g. fields to verify, documents required, fee
breakup):
- If the notice needs to list several discrete items, put each on its own line
  (use a line break between items), not run together in one sentence. You may
  prefix each with a plain hyphen "- ". Do not use numbered markdown headers.
- Bold the item label itself using **double asterisks**, e.g. "- **Full Name**"

Other rules:
- Do NOT start with "Dear Parents," — that greeting is already added separately by the template. Start directly with the first sentence of the notice.
- Keep the notice focused ONLY on the primary event given. Do not mention any
  other event unless explicitly told to include it.
- If told to include a secondary event, weave it in naturally as one extra
  sentence near the end, not as a separate disconnected paragraph.
- Bold key facts (date, day, timing, venue, amounts, deadlines) using **double asterisks**.
- End the body text before the closing — do NOT write "Regards" or the
  principal's name, that is added separately by the template.
- Output ONLY the notice body text. No headers, no markdown title, no signature."""


EXTRACTION_SYSTEM_PROMPT = """You extract structured fields from a school notice request.
Return ONLY valid JSON, no markdown fences, no commentary, in this exact shape:

{
  "event_title": {"value": "...", "missing": false},
  "date": {"value": "...", "missing": false},
  "timing": {"value": "...", "missing": false},
  "venue": {"value": "...", "missing": false},
  "classes": {"value": "...", "missing": false},
  "extra_context": {"value": "...", "missing": false}
}

Rules:
- Only mark missing:true if the user genuinely did not mention that detail anywhere.
- Do NOT invent values. If unsure, mark missing:true and leave value "".
- "extra_context" captures EVERYTHING else specific the user said that doesn't fit
  the other five fields — fee amounts and deadlines, required actions (e.g. visit
  the office, submit a form), lists of items/fields to verify or correct, special
  instructions, tone requests, conditions, exceptions, audience notes, etc.
  Preserve their wording and every distinct item closely — do not summarize a
  list down to fewer items than the user gave. If nothing extra was said, mark
  it missing:true.
- Dates/times: normalize obvious formats only if you are confident. If you cannot
  confidently resolve a relative date ("next Monday"), leave it as written rather
  than guessing an actual calendar date.
- Respond with JSON only. No preamble, no explanation, no markdown code fences."""


def extract_fields_from_prompt(prompt: str) -> dict:
    """Parse the user's free-text prompt into structured fields via the LLM.
    Returns {} on any failure so callers can fall back gracefully — but logs
    the failure so it doesn't disappear silently."""
    if not prompt or not prompt.strip():
        return {}

    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0,
            max_tokens=700,
        )
        raw = resp.choices[0].message.content.strip()
    except Exception:
        logger.exception("Groq extraction API call failed for prompt: %r", prompt)
        return {}

    cleaned = re.sub(r"^```(?:json)?|```$", "", raw, flags=re.MULTILINE).strip()

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        logger.error(
            "Groq extraction returned non-JSON output. raw_response=%r prompt=%r",
            raw, prompt,
        )
        return {}

    if not isinstance(parsed, dict):
        logger.error("Groq extraction returned JSON that wasn't an object: %r", parsed)
        return {}

    return parsed


def generate_notice_draft(
    primary_event,
    timing,
    venue,
    classes,
    include_events=None,
    event_title=None,
    date=None,
    raw_prompt="",
    extra_context="",
):
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

    if extra_context:
        context += f"\nAdditional details the user specifically mentioned (include ALL of these, do not drop any):\n{extra_context}\n"

    if raw_prompt:
        context += f"""
--- USER'S ORIGINAL REQUEST (ultimate source of truth) ---
{raw_prompt}
------------------------------------------------------------
The fields above are a normalized summary of this request. If anything above
conflicts with the original request, or the original request contains detail
not captured above (including any list of items, fees, or instructions),
follow the original request and include everything it specifies.
"""

    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": context},
            ],
            temperature=0.6,
            max_tokens=800,
        )
    except Exception:
        logger.exception("Groq generation API call failed. context=%r", context)
        raise

    return resp.choices[0].message.content.strip()