# PhishGuard-Family

## What is it?
A tool that helps people check if a suspicious text or email is a scam. You paste the message (or upload a screenshot), and it explains in simple language what looks wrong and what to do next.

## Who does it help?
Non-technical people, especially immigrant families, who find it hard to tell real messages from scams (fake CRA, Canada Post, bank, and job messages).

## Our Entry
- **Challenge:** Best Open-Source AI Project (main challenge)
- **Type:** a project built on an open-weight small language model (Gemma 3 4B, 4 billion parameters)
- **License:** MIT

## Languages
- English
- Urdu (اردو)
- Spanish (Español)
- Arabic (العربية)
- Hindi (हिन्दी)
- French (Français)

## Features
- **Clear verdict:** Scam, Suspicious or Safe, shown in red, yellow or green
- **Highlighted message:** the suspicious phrases are highlighted inside the message you pasted
- **Red flags and advice:** the warning signs, in simple words
- **What to do now:** fixed, never AI-generated steps, such as forwarding scam texts to 7726 and reporting to the Canadian Anti-Fraud Centre
- **Warn my family:** a short shareable warning with a copy button. It never includes names, phone numbers, emails or links from the original message.
- **Screenshot upload:** the model reads the text from a screenshot, then checks it
- **Example messages:** one-click examples (a fake package fee, a fake CRA message and a normal school reminder)
- **Accessibility:** Easy mode (bigger text), right-to-left layout for Urdu and Arabic, and a Read aloud button that uses the browser's voice
- **Privacy:** everything runs on the user's computer, and a status light shows whether the AI is running

## How it works
```
Message --> rules.py --> Gemma 3 4B via Ollama --> checker.py --> app.py
            instant      explains in the user's    merges the     shows the
            checks       language, using the       results        result
                         rule findings as evidence
```

1. The user pastes a suspicious message and picks a language.
2. **Rule checks run first** (`rules.py`). They catch known scam patterns for certain: gift card or crypto payments, threats of arrest, requests for a PIN or SIN, short links, lookalike links pretending to be CRA, Canada Post or a bank, and urgency. Some keywords are checked in several languages.
3. **The AI model explains** (`checker.py`, `prompts.py`). The rule findings are passed to Gemma as evidence. It returns a verdict, red flags, advice, exact phrases to highlight and a short family warning in the chosen language.
4. **The results are merged.** The rules can raise a verdict but never lower it, so the small model can't call a scam "safe". Highlights are kept only if they really appear in the message. If the model is not running, the app still shows the rule checks and never calls a message "Safe" without the AI.
5. **The family warning is cleaned.** Links, phone numbers and emails are removed, so it is safe to share.
6. **Fixed next steps** are shown in the chosen language (`resources.py`), so the phone numbers are always correct.
7. **The app** (`app.py`) shows the result using Streamlit. All model output is HTML-escaped before it is displayed.

## Model and license
| | |
|---|---|
| **Model** | Gemma 3 4B by Google, an open-weight small language model (10 billion parameters or fewer) |
| **Model terms** | [Gemma Terms of Use](https://ai.google.dev/gemma/terms) |
| **Runs with** | Ollama, model `gemma3:4b` |
| **This project's license** | MIT |

**Built by our team:** the prompt, the scam rules, the code that merges rules with the AI, the multi-language support and the app.

## Project files
| File | What it does |
|---|---|
| `app.py` | The Streamlit app people see |
| `checker.py` | Backend: runs the rules, asks the model, merges the results |
| `rules.py` | Scam rule checks that run before the AI |
| `prompts.py` | The instructions given to the model, in six languages |
| `resources.py` | Fixed "what to do" steps and privacy note in every language |

## How to run it
You need Python 3.9 or newer and [Ollama](https://ollama.com).

1. Install Ollama and open it (it must stay running).
2. Download the model:
```
   ollama pull gemma3:4b
```
3. Get the code:
```
   git clone https://github.com/mariyam-faisal/PhishGuard-Family.git
   cd PhishGuard-Family
```
4. Install the packages:
```
   pip install -r requirements.txt
```
5. Start the app:
```
   streamlit run app.py
```
6. Open http://localhost:8501 in your browser.

## Limitations
- It's a helper, not a guarantee. The app tells users to confirm with the real organization through its official website or phone number.
- A small model can make mistakes on unusual messages. The rule checks reduce that risk but don't remove it.
- It only reads the text. It doesn't open links or check websites.
- Read-aloud voices depend on the voices installed on the computer.

## Team
- **Basmah Khalid:** AI and prompts (prompt design, scam test messages, testing)
- **Areej Tariq:** Backend (Python code connecting the app to the model)
- **Hibbah Owais:** Frontend (the Streamlit app people see)
- **Mariyam Faisal:** GitHub, README and demo

## License
MIT. See the `LICENSE` file.

## Disclaimer
This is a helper, not a guarantee. When in doubt, contact the organization using its official website or phone number.
