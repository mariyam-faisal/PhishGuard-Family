"""
rules.py - Deterministic scam checks that run BEFORE the AI model.

    from rules import check_rules, flag_text
    hits = check_rules(text)
    # [{"code": "gift_card", "severity": "high", "match": "Google Play gift cards"}, ...]
    flag_text("gift_card", "ur")  # short explanation in that language

These are guaranteed catches: even if the small model misses something,
the rules still flag it. The model adds the explanation on top.
"""

import re
from urllib.parse import urlparse

# ---------------------------------------------------------------- patterns

URL_RE = re.compile(
    r"(?<![@\w])("
    r"https?://[^\s<>\"']+"
    r"|www\.[^\s<>\"']+"
    r"|(?:bit\.ly|tinyurl\.com|t\.co|goo\.gl|ow\.ly|is\.gd|buff\.ly|rebrand\.ly|cutt\.ly|"
    r"shorturl\.at|rb\.gy|tiny\.cc|t\.ly)/[^\s<>\"']*"
    r"|[a-z0-9][a-z0-9-]*(?:\.[a-z0-9-]+)*\.(?:com|ca|net|org|info|xyz|top|click|link|live|"
    r"online|site|shop|io|co|me|app|support|help|vip|cc|biz)(?:/[^\s<>\"']*)?"
    r")",
    re.IGNORECASE,
)

SHORTENERS = {
    "bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly", "is.gd", "buff.ly",
    "rebrand.ly", "cutt.ly", "shorturl.at", "rb.gy", "tiny.cc", "t.ly",
}

# Official domains. A link counts as official if its host is one of these
# or a subdomain of one (e.g. www.canada.ca, cra-arc.gc.ca).
OFFICIAL_DOMAINS = {
    "canada.ca", "gc.ca", "canadapost.ca", "canadapost-postescanada.ca",
    "purolator.com", "interac.ca",
    "rbc.com", "rbcroyalbank.com", "td.com", "tdcanadatrust.com",
    "scotiabank.com", "bmo.com", "cibc.com", "nationalbank.ca",
    "servicecanada.gc.ca", "ontario.ca", "serviceontario.ca",
}

BRANDS_RE = re.compile(
    r"\b(CRA|Canada Revenue|Revenue Canada|Service Canada|Canada Post|Postes Canada|"
    r"Purolator|Interac|RBC|Royal Bank|TD Bank|TD Canada|Scotiabank|BMO|CIBC|"
    r"National Bank|ServiceOntario|Immigration Canada|IRCC)\b",
    re.IGNORECASE,
)

KEYWORDS = {
    # code: (severity, regex)
    "gift_card": ("high", r"gift\s*-?\s*cards?|google\s*play\s*cards?|itunes\s*cards?|steam\s*cards?|"
                          r"گفٹ\s*کارڈ|गिफ्ट\s*कार्ड|cartes?-cadeaux|tarjetas?\s+de\s+regalo"),
    "crypto": ("high", r"bitcoin|btc|crypto(?:currency)?|usdt|ethereum|bitcoin\s*atm|بٹ\s*کوائن|बिटकॉइन"),
    "threat": ("high", r"arrest(?:ed)?|warrant|police|deport(?:ed|ation)?|jail|legal\s+action|lawsuit|"
                       r"court\s+case|گرفتار|پولیس|giraftar|गिरफ्तार|पुलिस|arrestation|poursuites?|polic[ií]a|arresto|detenci[oó]n"),
    "sensitive_info": ("high", r"\bSIN\b|social\s+insurance|\bPIN\b|password|passcode|card\s+number|"
                               r"\bCVV\b|verification\s+code|one[-\s]time\s+code|\bOTP\b|security\s+code|"
                               r"پاس\s*ورڈ|पासवर्ड|mot\s+de\s+passe|\bNIP\b|\bNAS\b|contrase[nñ]a|n[uú]mero\s+de\s+tarjeta"),
    "etransfer": ("medium", r"e-?\s*transfer|interac\s+transfer|send\s+(?:the\s+)?money|wire\s+transfer|"
                            r"virement|transferencia"),
    "urgency": ("medium", r"urgent(?:ly)?|immediately|right\s+away|final\s+(?:notice|warning)|last\s+warning|"
                          r"within\s+\d+\s+(?:hours?|hrs?|minutes?)|act\s+now|today\s+only|expires?\s+today|"
                          r"account\s+(?:is\s+|has\s+been\s+)?(?:locked|suspended|frozen|blocked)|"
                          r"فوری|fori|turant|तुरंत|immédiatement|urgente|inmediatamente"),
    "new_number": ("medium", r"new\s+(?:phone\s+)?number|lost\s+my\s+phone|broke\s+my\s+phone|"
                             r"(?:hi|hey|hola)\s+(?:mom|mum|dad|ammi|abbu|ammi\s*jaan|mam[aá]|pap[aá])|نیا\s+نمبر|naya\s+number|n[uú]mero\s+nuevo"),
}
KEYWORDS = {code: (sev, re.compile(pat, re.IGNORECASE)) for code, (sev, pat) in KEYWORDS.items()}

PHONE_RE = re.compile(r"(?:\+?1[\s.-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}")
CALL_RE = re.compile(r"\b(call|contact|phone|text)\b", re.IGNORECASE)
EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")

# ---------------------------------------------------------------- helpers


def _host(url):
    if not re.match(r"https?://", url, re.IGNORECASE):
        url = "http://" + url
    host = (urlparse(url).hostname or "").lower()
    return host[4:] if host.startswith("www.") else host


def _is_official(host):
    return any(host == d or host.endswith("." + d) for d in OFFICIAL_DOMAINS)


def find_urls(text):
    return [m.group(0).rstrip(".,!?;:)") for m in URL_RE.finditer(text)]


def strip_private(text):
    """Remove links, phone numbers and emails (used for the shareable family warning)."""
    text = EMAIL_RE.sub("", text)
    text = URL_RE.sub("", text)
    text = PHONE_RE.sub("", text)
    return re.sub(r"\s{2,}", " ", text).strip()


# ---------------------------------------------------------------- main check


def check_rules(text):
    """Return a list of rule hits: {"code", "severity", "match"} (one per code)."""
    if not text:
        return []
    hits = {}

    def add(code, severity, match):
        if code not in hits:
            hits[code] = {"code": code, "severity": severity, "match": match}

    # Links
    urls = find_urls(text)
    brand = BRANDS_RE.search(text)
    for url in urls:
        host = _host(url)
        if host in SHORTENERS:
            add("shortener", "high", url)
        elif brand and not _is_official(host):
            add("impersonation", "high", url)
        elif not _is_official(host):
            add("link", "medium", url)

    # Keywords
    for code, (severity, pattern) in KEYWORDS.items():
        m = pattern.search(text)
        if m:
            add(code, severity, m.group(0))

    # Phone number with "call / contact"
    phone = PHONE_RE.search(text)
    if phone and CALL_RE.search(text):
        add("call_now", "medium", phone.group(0))

    return list(hits.values())


# ---------------------------------------------------------------- explanations

FLAG_TEXT = {
    "en": {
        "link": "Has a link. Don't tap links in unexpected messages.",
        "shortener": "Uses a short link that hides the real website.",
        "impersonation": "Pretends to be an official organization, but links to an unofficial website.",
        "gift_card": "Asks for gift cards. Real organizations never take gift cards.",
        "crypto": "Asks for Bitcoin or crypto. This is a common scam.",
        "etransfer": "Asks you to send money by e-transfer.",
        "threat": "Threatens police, arrest or legal action to scare you.",
        "urgency": "Pushes you to act fast.",
        "sensitive_info": "Asks for private information like a PIN, password or SIN.",
        "call_now": "Asks you to call a phone number.",
        "new_number": "Says it's family on a new number. Call their old number to check.",
    },
    "ur": {
        "link": "اس میں لنک ہے۔ اچانک آنے والے پیغام کے لنک پر کلک نہ کریں۔",
        "shortener": "چھوٹا لنک استعمال کیا گیا ہے جو اصل ویب سائٹ چھپاتا ہے۔",
        "impersonation": "سرکاری ادارہ ہونے کا دعویٰ کرتا ہے، مگر لنک غیر سرکاری ویب سائٹ کا ہے۔",
        "gift_card": "گفٹ کارڈ مانگتا ہے۔ اصل ادارے کبھی گفٹ کارڈ نہیں لیتے۔",
        "crypto": "بٹ کوائن یا کرپٹو مانگتا ہے۔ یہ عام فراڈ ہے۔",
        "etransfer": "ای ٹرانسفر سے پیسے بھیجنے کا کہتا ہے۔",
        "threat": "ڈرانے کے لیے پولیس، گرفتاری یا قانونی کارروائی کی دھمکی دیتا ہے۔",
        "urgency": "آپ کو جلدی کرنے پر مجبور کرتا ہے۔",
        "sensitive_info": "پن، پاس ورڈ یا SIN جیسی ذاتی معلومات مانگتا ہے۔",
        "call_now": "کسی فون نمبر پر کال کرنے کا کہتا ہے۔",
        "new_number": "کہتا ہے کہ گھر والا نئے نمبر سے ہے۔ پرانے نمبر پر کال کر کے تصدیق کریں۔",
    },
    "es": {
        "link": "Tiene un enlace. No toque enlaces en mensajes inesperados.",
        "shortener": "Usa un enlace corto que esconde el sitio web real.",
        "impersonation": "Dice ser una organización oficial, pero el enlace lleva a un sitio no oficial.",
        "gift_card": "Pide tarjetas de regalo. Las organizaciones reales nunca aceptan tarjetas de regalo.",
        "crypto": "Pide Bitcoin o criptomonedas. Es una estafa común.",
        "etransfer": "Le pide enviar dinero por transferencia electrónica.",
        "threat": "Amenaza con policía, arresto o acciones legales para asustarle.",
        "urgency": "Le presiona para actuar rápido.",
        "sensitive_info": "Pide información privada como su PIN, contraseña o número de seguro social (SIN).",
        "call_now": "Le pide llamar a un número de teléfono.",
        "new_number": "Dice ser un familiar con un número nuevo. Llame a su número anterior para confirmar.",
    },
    "ar": {
        "link": "يحتوي على رابط. لا تضغط على الروابط في الرسائل غير المتوقعة.",
        "shortener": "يستخدم رابطًا مختصرًا يخفي الموقع الحقيقي.",
        "impersonation": "يدّعي أنه جهة رسمية، لكن الرابط لموقع غير رسمي.",
        "gift_card": "يطلب بطاقات هدايا. الجهات الحقيقية لا تقبل بطاقات الهدايا أبدًا.",
        "crypto": "يطلب بيتكوين أو عملات رقمية. هذا احتيال شائع.",
        "etransfer": "يطلب منك إرسال المال بالتحويل الإلكتروني.",
        "threat": "يهدد بالشرطة أو الاعتقال أو إجراءات قانونية لتخويفك.",
        "urgency": "يضغط عليك للتصرف بسرعة.",
        "sensitive_info": "يطلب معلومات خاصة مثل الرقم السري أو كلمة المرور أو رقم التأمين الاجتماعي.",
        "call_now": "يطلب منك الاتصال برقم هاتف.",
        "new_number": "يدّعي أنه أحد أفراد العائلة برقم جديد. اتصل برقمه القديم للتأكد.",
    },
    "hi": {
        "link": "इसमें लिंक है। अचानक आए मैसेज के लिंक पर क्लिक न करें।",
        "shortener": "छोटा लिंक है जो असली वेबसाइट छिपाता है।",
        "impersonation": "सरकारी संस्था होने का दावा करता है, लेकिन लिंक गैर-सरकारी वेबसाइट का है।",
        "gift_card": "गिफ्ट कार्ड मांगता है। असली संस्थाएं कभी गिफ्ट कार्ड नहीं लेतीं।",
        "crypto": "बिटकॉइन या क्रिप्टो मांगता है। यह आम धोखा है।",
        "etransfer": "ई-ट्रांसफर से पैसे भेजने को कहता है।",
        "threat": "डराने के लिए पुलिस, गिरफ्तारी या कानूनी कार्रवाई की धमकी देता है।",
        "urgency": "आपको जल्दी करने के लिए दबाव डालता है।",
        "sensitive_info": "PIN, पासवर्ड या SIN जैसी निजी जानकारी मांगता है।",
        "call_now": "किसी फ़ोन नंबर पर कॉल करने को कहता है।",
        "new_number": "कहता है कि परिवार का कोई सदस्य नए नंबर से है। पुराने नंबर पर कॉल करके पक्का करें।",
    },
    "fr": {
        "link": "Contient un lien. Ne cliquez pas sur les liens d'un message inattendu.",
        "shortener": "Utilise un lien court qui cache le vrai site.",
        "impersonation": "Se fait passer pour un organisme officiel, mais le lien mène à un site non officiel.",
        "gift_card": "Demande des cartes-cadeaux. Les vrais organismes n'acceptent jamais de cartes-cadeaux.",
        "crypto": "Demande du Bitcoin ou des cryptomonnaies. C'est une arnaque courante.",
        "etransfer": "Vous demande d'envoyer de l'argent par virement Interac.",
        "threat": "Menace de police, d'arrestation ou de poursuites pour vous faire peur.",
        "urgency": "Vous pousse à agir vite.",
        "sensitive_info": "Demande des informations privées comme un NIP, un mot de passe ou un NAS.",
        "call_now": "Vous demande d'appeler un numéro de téléphone.",
        "new_number": "Prétend être un proche avec un nouveau numéro. Appelez son ancien numéro pour vérifier.",
    },
}


def flag_text(code, language="en"):
    table = FLAG_TEXT.get(language, FLAG_TEXT["en"])
    return table.get(code) or FLAG_TEXT["en"].get(code, code)
