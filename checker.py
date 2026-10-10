"""
checker.py - Backend for the Phishing Checker for Parents.

Frontend usage:

    from checker import check_message, check_image, is_model_ready, warm_up
    warm_up()                                        # call once at app start (optional)
    result = check_message(text, language="ur")     # "en", "ur", "es", "ar", "hi", "fr"
    result = check_image(image_bytes, language="en") # screenshot upload (stretch goal)

result is always a dict:
    {
        "ok": True/False,             # False -> show result["error"]
        "verdict": "Scam" | "Suspicious" | "Safe",   # always English, use it for the colour
        "red_flags": [str, ...],      # in the chosen language, max 5
        "advice": str,                # in the chosen language
        "highlights": [str, ...],     # exact phrases from the original message
        "rule_hits": [str, ...],      # codes from rules.py, e.g. "gift_card"
        "family_warning": str,        # short shareable warning, no links/numbers
        "model_used": bool,           # False if only the rules ran (model unavailable)
        "warning": str | None,        # non-fatal note to show, e.g. "AI model not running"
        "error": str | None,
    }
check_image also adds "extracted_text".

How it works: rules.py runs first (guaranteed catches), then the local open-weight
model explains, then results are merged. The verdict can only be raised by the
rules, never lowered.

Test from the terminal:  python checker.py
"""

import json

try:
    import ollama
except ImportError:  # lets the rules still work before `pip install ollama`
    ollama = None

from rules import check_rules, flag_text, strip_private

# Open-weight model run locally with Ollama. Change here if the team picks another one.
MODEL = "gemma3:4b"

KEEP_ALIVE = "30m"   # keep the model in memory between checks, so the demo stays fast
MODEL_OPTIONS = {"temperature": 0.1, "num_predict": 400}

VALID_VERDICTS = {"Scam", "Suspicious", "Safe"}
MAX_FLAGS = 5

# ---------------------------------------------------------------- prompt
# Person 1 owns prompts.py. Until it exists, these fallbacks are used.

FALLBACK_LANGUAGES = {
    "en": "simple English",
    "ur": "simple Urdu, written in Urdu script",
    "es": "simple Spanish",
    "ar": "simple Arabic",
    "hi": "simple Hindi, written in Devanagari",
    "fr": "simple French",
}

FALLBACK_PROMPT = """You are a careful scam-detection helper for newcomer families in Canada.
A parent will paste a text message or email. Decide if it is a scam.

Common scams in Canada:
- Fake CRA (Canada Revenue Agency): threats of arrest, demands for gift cards, crypto or e-transfer, "refund" links.
- Fake Canada Post / courier: "package held", small fee, link to pay.
- Fake bank: "account locked", asks for password, PIN or card number, link to log in.
- Job scams: high pay for little work, buy equipment, deposit a cheque.
- Family emergency: "Mom it's me, new number, send money".

Red flags: urgency or threats, asking for passwords/PINs/SIN, gift cards or crypto,
strange links or sender addresses, offers that are too good to be true.
Real CRA, Canada Post and banks never ask for passwords or gift cards by text.

Reply ONLY with JSON in this exact shape:
{"verdict": "Scam" or "Suspicious" or "Safe",
 "red_flags": ["short red flag", "..."],
 "advice": "one or two short sentences telling the parent what to do",
 "highlights": ["exact suspicious phrase copied from the message", "..."],
 "family_warning": "one short sentence to warn family about this type of scam"}

Rules:
- "verdict" must be exactly Scam, Suspicious or Safe (in English).
- Write "red_flags", "advice" and "family_warning" in {language}.
- "highlights" must be copied word-for-word from the message, in its original language. Max 5.
- "family_warning" must NOT include names, links or phone numbers from the message.
- Very simple words. Max 4 red flags. If Safe, red_flags and highlights can be empty.
- If unsure, choose Suspicious, never Safe.
"""

try:
    from prompts import LANGUAGES, build_system_prompt  # written by Person 1
except ImportError:
    LANGUAGES = FALLBACK_LANGUAGES

    def build_system_prompt(language_code="en"):
        return FALLBACK_PROMPT.replace("{language}", LANGUAGES.get(language_code, LANGUAGES["en"]))

# Used when the model gives no advice / warning, or isn't running.
FALLBACK_ADVICE = {
    "en": "Don't click links, reply or pay. Contact the organization using its official website or phone number.",
    "ur": "لنک پر کلک نہ کریں، جواب نہ دیں اور پیسے نہ بھیجیں۔ ادارے سے اس کی سرکاری ویب سائٹ یا فون نمبر پر رابطہ کریں۔",
    "es": "No toque enlaces, no responda y no pague. Contacte a la organización por su sitio web o número de teléfono oficial.",
    "ar": "لا تضغط على الروابط ولا ترد ولا تدفع. تواصل مع الجهة عبر موقعها أو رقمها الرسمي.",
    "hi": "लिंक पर क्लिक न करें, जवाब न दें और पैसे न भेजें। संस्था से उसकी आधिकारिक वेबसाइट या फ़ोन नंबर पर संपर्क करें।",
    "fr": "Ne cliquez pas, ne répondez pas et ne payez pas. Contactez l'organisme par son site ou son numéro officiel.",
}

FALLBACK_FAMILY_WARNING = {
    "en": "⚠️ Scam alert: I got a scam message. If you get one like it, don't click links, reply or pay.",
    "ur": "⚠️ فراڈ سے ہوشیار: مجھے ایک جعلی پیغام ملا ہے۔ ایسا پیغام آئے تو لنک پر کلک نہ کریں، جواب نہ دیں اور پیسے نہ بھیجیں۔",
    "es": "⚠️ Alerta de estafa: recibí un mensaje falso. Si le llega uno parecido, no toque enlaces, no responda y no pague.",
    "ar": "⚠️ تحذير من احتيال: وصلتني رسالة احتيال. إذا وصلتك رسالة مثلها فلا تضغط على الروابط ولا ترد ولا تدفع.",
    "hi": "⚠️ धोखे से सावधान: मुझे एक नकली मैसेज मिला है। ऐसा मैसेज आए तो लिंक पर क्लिक न करें, जवाब न दें और पैसे न भेजें।",
    "fr": "⚠️ Alerte arnaque : j'ai reçu un message frauduleux. Si vous en recevez un pareil, ne cliquez pas, ne répondez pas et ne payez pas.",
}


# ---------------------------------------------------------------- helpers


def _error(message):
    return {
        "ok": False, "verdict": None, "red_flags": [], "advice": "", "highlights": [],
        "rule_hits": [], "family_warning": "", "model_used": False, "warning": None,
        "error": message,
    }


def _dedupe(items):
    seen, out = set(), []
    for item in items:
        key = item.strip().lower()
        if key and key not in seen:
            seen.add(key)
            out.append(item.strip())
    return out


def _exact_highlights(text, phrases):
    """Keep only phrases that really appear in the message, returned with the message's own casing."""
    lower = text.lower()
    out = []
    for phrase in phrases:
        phrase = str(phrase).strip().strip('"').strip()
        if len(phrase) < 3:
            continue
        i = lower.find(phrase.lower())
        if i != -1:
            out.append(text[i:i + len(phrase)])
    return _dedupe(out)[:MAX_FLAGS]


def _rule_hints(hits):
    """Tell the model what the automatic checks already found (in English, for the model)."""
    if not hits:
        return ""
    lines = [f'- {h["code"].replace("_", " ")}: "{h["match"]}"' for h in hits]
    return "\n\nAUTOMATIC CHECKS FOUND:\n" + "\n".join(lines)


def _ask_model(text, language, hits=()):
    """Return (data_dict_or_None, warning_or_None, fatal_error_or_None)."""
    if ollama is None:
        return None, "AI model library not installed (pip install ollama). Showing rule checks only.", None
    try:
        response = ollama.chat(
            model=MODEL,
            messages=[
                {"role": "system", "content": build_system_prompt(language)},
                {"role": "user", "content": "MESSAGE:\n" + text[:4000] + _rule_hints(hits)},
            ],
            format="json",
            options=MODEL_OPTIONS,
            keep_alive=KEEP_ALIVE,
        )
    except Exception as e:
        status = getattr(e, "status_code", None)
        if status == 404:
            return None, f"Model '{MODEL}' is not installed (run: ollama pull {MODEL}). Showing rule checks only.", None
        return None, "AI model isn't running (open the Ollama app). Showing rule checks only.", None

    try:
        data = json.loads(response["message"]["content"])
        if not isinstance(data, dict):
            raise ValueError
        return data, None, None
    except (json.JSONDecodeError, ValueError, KeyError, TypeError):
        return None, "The AI gave an unexpected answer. Showing rule checks only.", None


# ---------------------------------------------------------------- status helpers


def is_model_ready():
    """True if Ollama is running and the model is installed. Frontend can show a status dot."""
    if ollama is None:
        return False
    try:
        names = [m.get("model", m.get("name", "")) for m in ollama.list().get("models", [])]
    except Exception:
        try:
            names = [m.model for m in ollama.list().models]
        except Exception:
            return False
    return any(n == MODEL or n.startswith(MODEL + ":") or n.split(":latest")[0] == MODEL for n in names)


def warm_up():
    """Load the model into memory once at app start, so the first check isn't slow."""
    if ollama is None:
        return False
    try:
        ollama.generate(model=MODEL, prompt="hi", options={"num_predict": 1}, keep_alive=KEEP_ALIVE)
        return True
    except Exception:
        return False


# ---------------------------------------------------------------- main


def check_message(text, language="en"):
    """Check a suspicious message. Returns a dict (see top of file)."""
    if not text or not text.strip():
        return _error("Please paste a message to check.")
    text = text.strip()
    if language not in LANGUAGES:
        language = "en"

    # 1. Rules (always run)
    hits = check_rules(text)
    high = sum(1 for h in hits if h["severity"] == "high")

    # 2. Model
    data, warning, _ = _ask_model(text, language, hits)
    model_used = data is not None

    if not model_used and not hits:
        # Nothing to go on: never call a message "Safe" without the model.
        return _error(warning or "Couldn't check this message. Please try again.")

    data = data or {}

    # 3. Verdict: model's verdict, raised (never lowered) by the rules
    verdict = str(data.get("verdict", "")).strip().capitalize()
    if verdict not in VALID_VERDICTS:
        verdict = "Suspicious"
    if high >= 2:
        verdict = "Scam"
    elif high == 1 and verdict == "Safe":
        verdict = "Suspicious"
    elif not model_used and hits and verdict == "Safe":
        verdict = "Suspicious"

    # 4. Red flags: rule explanations first, then the model's
    model_flags = data.get("red_flags") or []
    if isinstance(model_flags, str):
        model_flags = [model_flags]
    red_flags = _dedupe(
        [flag_text(h["code"], language) for h in hits] + [str(f) for f in model_flags]
    )[:MAX_FLAGS]

    # 5. Highlights: rule matches + model phrases, only if they're really in the text
    model_highlights = data.get("highlights") or []
    if isinstance(model_highlights, str):
        model_highlights = [model_highlights]
    highlights = _exact_highlights(text, [h["match"] for h in hits] + list(model_highlights))

    # 6. Advice and family warning (no links / numbers ever leak into the warning)
    advice = str(data.get("advice", "")).strip() or FALLBACK_ADVICE.get(language, FALLBACK_ADVICE["en"])
    family_warning = ""
    if verdict != "Safe":
        family_warning = strip_private(str(data.get("family_warning", "")))
        if len(family_warning) < 10:
            family_warning = FALLBACK_FAMILY_WARNING.get(language, FALLBACK_FAMILY_WARNING["en"])

    return {
        "ok": True,
        "verdict": verdict,
        "red_flags": red_flags,
        "advice": advice,
        "highlights": highlights,
        "rule_hits": [h["code"] for h in hits],
        "family_warning": family_warning,
        "model_used": model_used,
        "warning": warning,
        "error": None,
    }


def check_image(image_bytes, language="en"):
    """Stretch goal: read a screenshot with the model, then check the extracted text."""
    if not image_bytes:
        return _error("Please upload a screenshot.")
    if ollama is None:
        return _error("AI model library not installed. Run: pip install ollama")
    try:
        response = ollama.chat(
            model=MODEL,
            messages=[{
                "role": "user",
                "content": "Copy the text of the message in this screenshot exactly, word for word. "
                           "Output ONLY the message text, nothing else.",
                "images": [image_bytes],
            }],
            options={"temperature": 0},
            keep_alive=KEEP_ALIVE,
        )
        extracted = response["message"]["content"].strip()
    except Exception:
        return _error("Couldn't read the screenshot. Make sure Ollama is running, or paste the text instead.")

    if len(extracted) < 5:
        return _error("No message text found in the screenshot. Try pasting the text instead.")

    result = check_message(extracted, language)
    result["extracted_text"] = extracted
    return result


# ---------------------------------------------------------------- terminal test

if __name__ == "__main__":
    tests = [
        ("CRA: You owe $1,450 in back taxes. Pay today with Google Play gift cards or police will be sent to your address. Call 1-888-555-0199.", "en"),
        ("Canada Post: Your package is on hold due to unpaid fee of $1.99. Pay now: http://canadapost-redelivery.info", "ur"),
        ("Hi Mom, I lost my phone, this is my new number. Can you e-transfer me $400 urgently?", "es"),
        ("RBC: Your account is locked. Verify your card number and PIN at bit.ly/rbc-verify", "ar"),
        ("Hi, this is Ms. Khan from Riverdale Public School. Reminder that picture day is this Thursday.", "en"),
    ]
    for text, lang in tests:
        print("=" * 70)
        print(f"[{lang}] {text}")
        print(json.dumps(check_message(text, lang), ensure_ascii=False, indent=2))
