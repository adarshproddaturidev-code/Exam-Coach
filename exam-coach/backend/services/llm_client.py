"""
LLM Client — wraps the OpenAI v1 SDK with a graceful fallback to template responses.
"""
import os, json
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

_API_KEY  = os.getenv("OPENAI_API_KEY", "")
_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
_MODEL    = os.getenv("LLM_MODEL", "gpt-4o-mini")

_client = None
if _API_KEY and not _API_KEY.startswith("sk-your"):
    try:
        from openai import OpenAI
        _client = OpenAI(api_key=_API_KEY, base_url=_BASE_URL)
    except Exception:
        _client = None


def _chat(system_prompt: str, user_prompt: str):
    if _client is None:
        return None
    try:
        resp = _client.chat.completions.create(
            model=_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_prompt},
            ],
            temperature=0.7,
            max_tokens=2000,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        print(f"[LLM error] {e}")
        return None


# ── Study Plan ────────────────────────────────────────────────────────────────
def generate_study_plan(weak_topics: list[dict]) -> dict:
    """Return a 7-day plan dict. Falls back to template if no LLM."""
    topics_summary = "\n".join(
        f"- {t['topic']} ({t['subject']}): weakness={t['weakness_score']:.2f}, "
        f"error_rate={t['error_rate']*100:.0f}%"
        for t in weak_topics[:8]
    )

    system = (
        "You are an expert entrance exam coach. "
        "Respond ONLY with a valid JSON object, no markdown, no extra text. "
        'The JSON must look like: {"days": [{"day": 1, "date_label": "Day 1", '
        '"focus": "Topic name", "duration_hours": 2, "practice_questions": 20, '
        '"revision_blocks": ["Block 1","Block 2"], "tip": "Motivating tip."}]}'
    )
    user = (
        f"Create a 7-day personalised study plan for a student with these weak topics:\n{topics_summary}\n"
        "Prioritise weaker topics more. Make the plan motivational, specific, and actionable. "
        "Return ONLY valid JSON, no markdown fences."
    )

    raw = _chat(system, user)
    if raw:
        try:
            # Strip markdown fences if model adds them
            cleaned = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
            return json.loads(cleaned)
        except Exception:
            pass

    # ── Template fallback ──────────────────────────────────────────────────
    days = []
    top = weak_topics[:7] if weak_topics else [{"topic": "General Revision", "subject": "All", "weakness_score": 0.5}]
    for i in range(7):
        t = top[i % len(top)]
        score = t.get("weakness_score", 0.5)
        hours = round(1.5 + score * 2.5, 1)
        days.append({
            "day": i + 1,
            "date_label": f"Day {i+1}",
            "focus": t["topic"],
            "duration_hours": hours,
            "practice_questions": int(15 + score * 25),
            "revision_blocks": [
                f"Concept review: {t['topic']}",
                "Solve practice problems",
                "Timed mini-test (10 questions)",
                "Review mistakes & notes",
            ],
            "tip": f"Focus on understanding the fundamentals of {t['topic']}. "
                   f"Each mistake is a step closer to mastery! 💪",
        })
    return {"days": days}


# ── Recommendations ───────────────────────────────────────────────────────────
def generate_recommendations(weak_topics: list[dict]) -> dict:
    """Return recommendations dict. Falls back to template if no LLM."""
    topics_summary = "\n".join(
        f"- {t['topic']} ({t['subject']}): error_rate={t['error_rate']*100:.0f}%"
        for t in weak_topics[:6]
    )

    system = (
        "You are an expert entrance exam coach. "
        "Respond ONLY with valid JSON, no markdown fences. "
        'Format: {"recommendations": [{"topic": "...", "subject": "...", '
        '"why_weak": "...", "concept_revision": ["..."], '
        '"practice_exercises": ["..."], "mock_tests": ["..."], '
        '"resources": [{"type": "youtube|article", "title": "...", "url": "..."}], '
        '"improvement_tip": "..."}]}'
    )
    user = (
        f"Generate study material recommendations for these weak topics:\n{topics_summary}\n"
        "For each topic, explain why it might be weak and give specific, actionable resources. "
        "Return ONLY valid JSON."
    )

    raw = _chat(system, user)
    if raw:
        try:
            cleaned = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
            return json.loads(cleaned)
        except Exception:
            pass

    # ── Template fallback ──────────────────────────────────────────────────
    recs = []
    for t in weak_topics[:6]:
        recs.append({
            "topic": t["topic"],
            "subject": t["subject"],
            "why_weak": (
                f"You answered {t['error_rate']*100:.0f}% of {t['topic']} questions incorrectly. "
                f"Average time taken was {t['avg_time']:.1f}s, indicating "
                + ("slow recall — practice timed drills." if t['avg_time'] > 60 else "careless errors — review fundamentals.")
            ),
            "concept_revision": [
                f"Re-read the {t['topic']} chapter from your NCERT/standard textbook",
                f"Summarise key formulas and theorems for {t['topic']}",
                "Create flashcards for important concepts",
            ],
            "practice_exercises": [
                f"Solve 30 previous year questions on {t['topic']}",
                f"Complete 2 topic-wise tests on {t['topic']}",
                "Attempt mixed difficulty questions (easy → hard)",
            ],
            "mock_tests": [
                f"Take a 20-question timed mini-test on {t['topic']}",
                "Include this topic in the next full-length mock exam",
            ],
            "resources": [
                {
                    "type": "youtube",
                    "title": f"{t['topic']} — Full Concept Revision",
                    "url": f"https://www.youtube.com/results?search_query={t['topic'].replace(' ', '+')}+entrance+exam",
                },
                {
                    "type": "article",
                    "title": f"{t['topic']} — Notes & Formulas",
                    "url": f"https://www.google.com/search?q={t['topic'].replace(' ', '+')}+entrance+exam+notes",
                },
            ],
            "improvement_tip": (
                f"Break {t['topic']} into sub-topics. Master one sub-topic per day "
                "and link concepts together to build lasting understanding. You've got this! 🌟"
            ),
        })
    return {"recommendations": recs}
