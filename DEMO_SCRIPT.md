# Demo script (about 2 minutes)

**Before recording:**
- Open Ollama and run `streamlit run app.py`
- Check that the app says **PhishGuard-Family** everywhere
- Run each example once so the model is warmed up and answers quickly on camera
- Do a 10-second test recording to make sure your voice is captured
- Have the GitHub repo open in another tab

**Record on Windows:** press `Win + Shift + R` (Snipping Tool screen recording), or use OBS if your voice isn't captured.

---

**0:00 – The problem and the team (25 sec)**
"Scam texts pretending to be the CRA, Canada Post or a family member hit newcomer families and parents the hardest. Many aren't comfortable with English, and most scam tools are English-only. So we built PhishGuard-Family. We're four students, and we built the rules, prompts, backend and app ourselves."

**0:25 – English scam (30 sec)**
Click **📦 Package fee** → **Check message**.
"It says Scam. It highlights exactly what's wrong: the fake fee, the 24-hour pressure, and a link that looks like Canada Post but isn't. Then it shows real steps: forward to 7726 and report to the Anti-Fraud Centre."

**0:55 – Same scam, another language (25 sec)**
Switch the language to **اردو** → click **Check message** again.
"One switch, and the whole answer comes back in simple Urdu, right-to-left, so a parent can read it themselves. It also works in Spanish, Arabic, Hindi and French."
Optional: click **🔊 Read aloud** (skip it if the voice sounds wrong).

**1:20 – Warn my family + safe message (20 sec)**
Point at **Warn my family**: "One copy, and she can warn the whole family chat, without ever forwarding the scam link."
Click **🏫 School reminder** → **Check message**: "And a normal message comes back as safe, so it doesn't just flag everything."

**1:40 – How it works (25 sec)**
"Two layers. Rule checks catch known scam signs like lookalike links, gift cards and threats. Then Gemma 3 4B, Google's open-weight model, explains it in the parent's language. The rules can only make a warning stronger, never weaker. It all runs locally with Ollama, so private messages never leave the laptop."
**Switch to the GitHub repo tab for 3 seconds.**
"It's MIT licensed, public on GitHub, and the model and its license link are in our README."

**2:05 – Close (5 sec)**
"PhishGuard-Family: scam checking in your own language."

---

**If a judge asks "why open-weight?"** Privacy (messages contain personal details), works offline, free to run, and anyone can audit or improve it.

**If a judge asks "how accurate?"** We tested it on our own set of real-style scam and safe messages. (Only show `tests/results.md` if Person 1 has run `python run_tests.py` and the file exists.)
