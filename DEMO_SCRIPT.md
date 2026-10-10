# Demo script (about 2 minutes)

**Before recording:** open Ollama, run `streamlit run app.py`, and check each example once so the model is warmed up and answers quickly on camera.

**Record on Windows:** press `Win + Shift + R` (Snipping Tool screen recording), or use OBS.

---

**0:00 – The problem (20 sec)**
"Scam texts pretending to be the CRA, Canada Post or a family member hit newcomer families and parents the hardest. Many aren't comfortable with English, and almost every scam tool is English-only. So we built PhishGuard, with a little goldfish knight to guard your family from phishing."

**0:20 – English scam (30 sec)**
Click **📦 Package fee** → **Check message**. (While it thinks: "It runs right here on the laptop, so nothing goes online.")
"It says Scam. It highlights exactly what's wrong: the fake fee, the 24-hour pressure, and a link that looks like Canada Post but isn't. Then it shows real steps: forward to 7726 and report to the Anti-Fraud Centre."

**0:50 – Same scam, another language (25 sec)**
Switch the language to **اردو** → **Check message**.
"One switch, and the whole answer comes back in simple Urdu, right-to-left, so a parent can read it themselves. It also works in Spanish, Arabic, Hindi and French."
Optional: click **🔊 Read aloud**, or turn on **Aa Make text bigger**.

**1:15 – Warn my family + safe message (20 sec)**
Point at **Warn my family**: "One copy, and she can warn the whole family chat, without ever forwarding the scam link."
Click **🏫 School reminder** → **Check message**: "And a normal message comes back as safe, so it doesn't just flag everything."

**1:35 – How it works (20 sec)**
"Two layers. Rule checks catch known scam signs like lookalike links, gift cards and threats. Then Gemma 3 4B, Google's open-weight model, explains it in the parent's language. The rules can only make a warning stronger, never weaker. It all runs locally with Ollama, so private messages never leave the laptop. MIT licensed, on GitHub."

**1:55 – Close (5 sec)**
"PhishGuard: check before you trust, in your own language."

---

**If a judge asks "why open-weight?"** Privacy (messages contain personal details), works offline, free to run, and anyone can audit or improve it.

**If a judge asks "how accurate?"** Show `tests/results.md` from `python run_tests.py`.
