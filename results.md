# Test results

Model: Gemma 3 4B (local, via Ollama) · 14 test messages

**Accuracy: 14/14 (100%)** · Scams marked Safe: 0 · Family warnings leaking details: 0

| # | Message | Language | Expected | Got | ✓/✗ | Family warning clean |
|---|---|---|---|---|---|---|
| 1 | CRA NOTICE: You owe $1,240 in unpaid taxes. … | en | Scam | Scam | ✓ | ✓ |
| 2 | Canada Revenue Agency: You are eligible for … | en | Scam | Scam | ✓ | ✓ |
| 3 | Canada Post: Your package is on hold due to … | en | Scam | Scam | ✓ | ✓ |
| 4 | آپ کا ٹی ڈی بینک اکاؤنٹ عارضی طور پر بند کر … | ur | Scam | Scam | ✓ | ✓ |
| 5 | INTERAC e-Transfer: You have received $350.0… | en | Scam | Scam | ✓ | ✓ |
| 6 | گھر بیٹھے روزانہ 300 ڈالر کمائیں! کوئی تجربہ… | ur | Scam | Scam | ✓ | ✓ |
| 7 | Hi Mom, it's me. I dropped my phone and this… | en | Scam | Scam | ✓ | ✓ |
| 8 | میرے ساتھ بٹ کوائن میں صرف 500 ڈالر لگائیں ا… | ur | Scam | Scam | ✓ | ✓ |
| 9 | Reminder from Maple Grove Public School: Pic… | en | Safe | Safe | ✓ | ✓ |
| 10 | Reminder: You have an appointment with Dr. P… | en | Safe | Safe | ✓ | ✓ |
| 11 | السلام علیکم بہن، کل شام ہمارے گھر چائے پر آ… | ur | Safe | Safe | ✓ | ✓ |
| 12 | Canada Post: Your parcel was delivered to yo… | en | Safe | Safe | ✓ | ✓ |
| 13 | Hola mamá, soy yo. Se me rompió el teléfono … | es | Scam | Scam | ✓ | ✓ |
| 14 | Hola vecina, el sábado hacemos una cena en c… | es | Safe | Safe | ✓ | ✓ |
