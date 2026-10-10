# 🛡️ Hoshiyar · ہوشیار

**Paste a suspicious text or email. Get a clear answer in your own language, from an AI that runs entirely on your own computer.**

*Hoshiyar* means "alert" or "careful" in Urdu and Hindi.

Built at **Hacktoberfest x ElleHacks Hack Day** (October 10, 2026) for the *Best Open-Source AI Project* challenge.

![Hoshiyar screenshot](docs/screenshot.png)

---

## The problem

Scam texts pretending to be the CRA, Canada Post, banks or family members are everywhere, and they hit newcomer families and older parents hardest. Many aren't comfortable reading English fine print, and almost every scam-awareness tool is English-only.

## What Hoshiyar does

1. You paste a message you received, or upload a **screenshot** of it.
2. It answers **Scam**, **Suspicious** or **Looks safe**, with a colour, an icon and a word (never colour alone).
3. It **highlights the exact suspicious phrases** in the message, like a fake link or "pay within 24 hours".
4. It explains the **red flags** and **what this means** in short, simple sentences.
5. It shows fixed, trusted **"What to do now"** steps: forward to **7726**, report to the **Canadian Anti-Fraud Centre (1-888-495-8501)**, call your bank.
6. **Warn my family**: a short warning to copy into the family group chat. It never includes the scam's link, phone number or email.
7. Works in **6 languages**: English, اردو Urdu, Español, العربية Arabic, हिन्दी Hindi, Français. Urdu and Arabic use right-to-left layout.

## Who it helps

- Parents and grandparents who get scam texts but aren't sure what's real
- Newcomer families in Canada who read best in their own language
- People with low vision or low literacy: **Easy mode** (bigger text), **Read aloud**, the Atkinson Hyperlegible font, high contrast and large buttons
- Community groups (schools, mosques, settlement services) who want a simple tool to share

## Why an open-weight model, running locally

Scam messages often contain names, addresses and account details. Hoshiyar runs **Gemma 3 4B on the laptop with Ollama**, so **the message never leaves the computer**. It also works offline and costs nothing to run.

## How it works

```
Message ──► rules.py (instant checks) ──► Gemma 3 4B via Ollama (prompts.py) ──► checker.py merges ──► app.py shows it
              fake links, gift cards,        explains in the user's language,
              threats, urgency, PIN/SIN...   using the rule findings as evidence
```

Two layers working together:

- **`rules.py`: rule-based checks (no AI).** Regex checks catch what we know is a scam signal: lookalike links (`canadapost-redelivery.info` isn't Canada Post), short links (bit.ly), gift cards, crypto, threats of arrest, urgency, requests for a PIN/password/SIN, "Mom, it's my new number". Includes keywords in several languages.
- **Gemma 3 4B: explanation.** The rule findings are passed to the model as evidence. It returns JSON with a verdict, red flags, advice, exact phrases to highlight and a family warning, in the chosen language.
- **`checker.py`: the merge.** Rules can **raise** the verdict but never lower it, so the small model can't call a scam "safe". Highlights are kept only if they really appear in the message. Links, phone numbers and emails are stripped from the family warning. If the model isn't running, the app still shows the rule results.
- **`resources.py`:** fixed "What to do now" steps and the privacy note in all 6 languages, never AI-generated, so the phone numbers are always correct.
- **`app.py`:** the Streamlit interface. All model output is HTML-escaped before display.

## Model and license

| | |
|---|---|
| **Model** | **Gemma 3 4B** by Google: open-weight **small language model** (≤ 10B parameters) |
| **Model terms** | [Gemma Terms of Use](https://ai.google.dev/gemma/terms) |
| **Runs with** | [Ollama](https://ollama.com), model `gemma3:4b` |
| **This project's license** | [MIT](LICENSE) |

### Key dependencies

- [Streamlit](https://streamlit.io): web interface (Apache-2.0)
- [ollama-python](https://github.com/ollama/ollama-python): talks to the local model (MIT)
- Google Fonts: Atkinson Hyperlegible, Bricolage Grotesque, Noto Nastaliq Urdu, Noto Naskh Arabic (SIL Open Font License)

## How to run it

**1. Install Ollama and the model.** Download Ollama from [ollama.com/download](https://ollama.com/download), open it, then:

```bash
ollama pull gemma3:4b
```

**2. Install the Python packages:**

```bash
pip install -r requirements.txt
```

**3. Start the app:**

```bash
streamlit run app.py
```

It opens at <http://localhost:8501>.

## Testing

```bash
python checker.py      # 5 example messages, printed as JSON
python run_tests.py    # 14 labelled test messages in English, Urdu and Spanish
```

`run_tests.py` reports accuracy, how many scams were wrongly marked Safe, and whether any family warning leaked a link or number. Results are saved to `tests/results.md`.

**Our results:** see [tests/results.md](tests/results.md).

## Limitations

- It's a helper, not a guarantee. The app tells users to confirm with the real organization through its official website or phone number.
- A small model can make mistakes on unusual messages; the rule checks reduce, but don't remove, that risk.
- It only reads the text; it doesn't open links or check websites.
- Read-aloud voices depend on the voices installed on the computer.

## Next steps

- More languages (Punjabi, Tamil, Tagalog, Chinese), each checked by a native speaker
- A browser extension or phone share-sheet so people can check a message in one tap
- A "scam of the week" card for community groups

## Team

- [Name]: AI & prompts (`prompts.py`, `resources.py`, tests)
- [Name]: backend (`checker.py`, `rules.py`)
- [Name]: frontend (`app.py`)
- [Name]: GitHub, README & demo
