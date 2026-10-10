# PhishGuard-Family

## What is it?
A tool that helps people check if a suspicious text or email is a scam. 
You paste the message, and it explains in simple language what 
looks wrong and what to do next.

## Who does it help?
Non-technical people, especially immigrant families, who find it hard to 
tell real messages from scams (fake CRA, Canada Post, bank, and job messages).

## Languages
- English
- Urdu (اردو)
- Arabic (العربية)
- Hindi (हिन्दी)
- French (Français)
- Spanish (Español)

## Features
- **Clear verdict:** Scam, Suspicious or Safe, shown in red, yellow or green
- **Red flags:** the warning signs found in the message, in simple words
- **What to do next:** short, practical steps
- **Warn my family:** a short shareable warning that never includes names,
  phone numbers or links from the original message. It can be copied or sent
  through WhatsApp.
- **Accessibility:** Easy mode (larger text, higher contrast), right-to-left
  layout for Urdu and Arabic, and a Read aloud button

## How it works
1. The user pastes a suspicious message and picks a language.
2. **Rule checks run first** (`rules.py`). They catch known scam patterns for
   certain: gift card or crypto payments, threats of arrest, requests for a
   PIN or SIN, short links, and fake links pretending to be CRA, Canada Post
   or a bank.
3. **The AI model explains** (`checker.py`). Gemma reads the message and the
   rule findings, then returns a verdict, red flags, advice, and a short
   family warning in the chosen language.
4. **The results are merged.** The rules can raise a verdict but never lower
   it. If the model is not running, the app still shows the rule checks and
   never calls a message "Safe" without the AI.
5. **The family warning is cleaned.** Links, phone numbers and emails are
   removed, so it is safe to share.
6. **Fixed next steps** (such as reporting to the Canadian Anti-Fraud Centre)
   are shown in the chosen language (`resources.py`).

Everything runs on the user's own computer. Messages are never sent online.

## Model used
- **Model:** Gemma 3 4B (`gemma3:4b`), an open-weight model, run locally
  with Ollama
- **Size:** 4 billion parameters, so it is a small language model (10 billion
  or fewer)
- **License / terms:** https://ai.google.dev/gemma/terms
- **Built by our team:** the prompt, the scam rules, the code that merges
  rules with the AI, the multi-language support, and the test script

## Test results
(TO FILL IN LATER)

## How to run it
(TO FILL IN LATER)

## Team
(TO FILL IN LATER)
