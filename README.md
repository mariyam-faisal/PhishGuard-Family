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
2. The app sends it to the Gemma model running locally with Ollama.
3. The model returns a verdict, red flags, advice and a family warning.
4. The app shows the result in the chosen language.

## Model used
- **Model:** Gemma (open-weight), run locally with Ollama
- **License / terms:** https://ai.google.dev/gemma/terms

## How to run it
(TO FILL IN LATER)

## Team
(TO FILL IN LATER)
