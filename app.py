"""
app.py - PhishGuard: the scam checker web app (Streamlit).

Run:  streamlit run app.py      (opens at http://localhost:8501)

Uses checker.py (rules + local Gemma 3 4B) and resources.py (fixed "what to do" text).
Images live in assets/.
"""

import base64
import html
import json
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from checker import MODEL, check_image, check_message, is_model_ready, warm_up

try:
    from resources import ACTION_STEPS, PRIVACY_NOTE
except ImportError:  # fallback until resources.py is in the folder
    ACTION_STEPS = {"en": [
        "Don't click links, reply, or pay.",
        "Forward scam texts to 7726 (SPAM).",
        "Report it to the Canadian Anti-Fraud Centre: 1-888-495-8501.",
        "Call your bank using the number on the back of your card.",
    ]}
    PRIVACY_NOTE = {"en": "Your message is checked only on this laptop. It is never sent online."}

HERE = Path(__file__).parent
ICON = HERE / "assets" / "phishguard-icon.png"
MASCOT = HERE / "assets" / "phishguard-mascot.png"

st.set_page_config(page_title="PhishGuard", page_icon=str(ICON) if ICON.exists() else "🛡️",
                   layout="centered")

# ---------------------------------------------------------------- languages

LANG_OPTIONS = {  # label shown -> code used by checker.py
    "English": "en", "اردو": "ur", "Español": "es",
    "العربية": "ar", "हिन्दी": "hi", "Français": "fr",
}
RTL = {"ur", "ar"}
SPEECH_LANG = {"en": "en-CA", "ur": "ur-PK", "es": "es-ES", "ar": "ar-SA", "hi": "hi-IN", "fr": "fr-CA"}

UI = {
    "en": {
        "headline": "Not sure about a message?",
        "sub": "Paste it below. We'll help you check it.",
        "label": "Paste your text or email here",
        "placeholder": "Touch here and paste the message you received…",
        "check": "Check message", "upload_link": "Or upload a screenshot",
        "upload_label": "Choose a screenshot of the message (PNG or JPG)",
        "shot_button": "Check screenshot", "reading": "Reading the screenshot…",
        "examples": "Try an example:", "checking": "Checking the message… this can take about 20 seconds.",
        "empty": "Please paste a message first.",
        "stays": "Your message stays on your device.",
        "help": "Need help pasting a message?",
        "help_body": "1. Open the message on your phone.\n\n2. Press and hold the text, then tap **Copy**.\n\n3. Come back here, press and hold the box, then tap **Paste**.\n\nOr take a screenshot and upload it.",
        "bigger": "Make text bigger", "helper": "A helper, not a guarantee.",
        "result": "RESULT", "scam": "Scam", "suspicious": "Suspicious", "safe": "Looks safe",
        "scam_meaning": "This is very likely a scam. Don't click links, reply, or pay.",
        "suspicious_meaning": "Something looks wrong. Don't click or pay until you check with the real organization.",
        "safe_meaning": "We didn't find warning signs. Still, never share passwords or codes.",
        "noticed": "What we noticed in the message", "advice": "What this means",
        "todo": "What to do now", "family": "Warn my family",
        "family_sub": "A safe warning to paste in your family chat. It never includes the scam link.",
        "read_aloud": "Read aloud", "ai_ready": "AI ready", "ai_off": "AI off · rule checks only",
        "extracted": "Text we read from the screenshot",
        "disclaimer": "When in doubt, contact the organization using its official website or phone number.",
    },
    "ur": {
        "headline": "کیا آپ کو کسی پیغام پر شک ہے؟",
        "sub": "اسے نیچے پیسٹ کریں۔ ہم چیک کرنے میں آپ کی مدد کریں گے۔",
        "label": "اپنا پیغام یا ای میل یہاں پیسٹ کریں",
        "placeholder": "یہاں ٹیپ کریں اور ملنے والا پیغام پیسٹ کریں…",
        "check": "پیغام چیک کریں", "upload_link": "یا اسکرین شاٹ اپ لوڈ کریں",
        "upload_label": "پیغام کا اسکرین شاٹ منتخب کریں (PNG یا JPG)",
        "shot_button": "اسکرین شاٹ چیک کریں", "reading": "اسکرین شاٹ پڑھا جا رہا ہے…",
        "examples": "مثال آزمائیں:", "checking": "پیغام چیک کیا جا رہا ہے… اس میں تقریباً 20 سیکنڈ لگ سکتے ہیں۔",
        "empty": "پہلے کوئی پیغام پیسٹ کریں۔",
        "stays": "آپ کا پیغام آپ کے آلے پر ہی رہتا ہے۔",
        "help": "پیغام پیسٹ کرنے میں مدد چاہیے؟",
        "help_body": "۱۔ اپنے فون پر پیغام کھولیں۔\n\n۲۔ متن کو دبا کر رکھیں، پھر **کاپی** پر ٹیپ کریں۔\n\n۳۔ یہاں واپس آئیں، خانے کو دبا کر رکھیں، پھر **پیسٹ** پر ٹیپ کریں۔\n\nیا اسکرین شاٹ لے کر اپ لوڈ کریں۔",
        "bigger": "متن بڑا کریں", "helper": "یہ مدد ہے، گارنٹی نہیں۔",
        "result": "نتیجہ", "scam": "فراڈ", "suspicious": "مشکوک", "safe": "محفوظ لگتا ہے",
        "scam_meaning": "یہ تقریباً یقینی طور پر فراڈ ہے۔ لنک پر کلک نہ کریں، جواب نہ دیں اور پیسے نہ بھیجیں۔",
        "suspicious_meaning": "کچھ گڑبڑ لگتی ہے۔ اصل ادارے سے تصدیق کیے بغیر کلک نہ کریں اور پیسے نہ دیں۔",
        "safe_meaning": "ہمیں خطرے کی کوئی نشانی نہیں ملی۔ پھر بھی کبھی پاس ورڈ یا کوڈ کسی کو نہ دیں۔",
        "noticed": "پیغام میں ہمیں کیا نظر آیا", "advice": "اس کا مطلب",
        "todo": "اب کیا کریں", "family": "گھر والوں کو خبردار کریں",
        "family_sub": "فیملی گروپ میں بھیجنے کے لیے محفوظ پیغام۔ اس میں فراڈ والا لنک کبھی شامل نہیں ہوتا۔",
        "read_aloud": "سنیں", "ai_ready": "AI تیار ہے", "ai_off": "AI بند ہے · صرف خودکار جانچ",
        "extracted": "اسکرین شاٹ سے پڑھا گیا متن",
        "disclaimer": "شک ہو تو ادارے سے اس کی سرکاری ویب سائٹ یا فون نمبر کے ذریعے رابطہ کریں۔",
    },
    "es": {
        "headline": "¿No está seguro de un mensaje?",
        "sub": "Péguelo abajo. Le ayudamos a revisarlo.",
        "label": "Pegue aquí su mensaje o correo",
        "placeholder": "Toque aquí y pegue el mensaje que recibió…",
        "check": "Revisar mensaje", "upload_link": "O suba una captura de pantalla",
        "upload_label": "Elija una captura de pantalla del mensaje (PNG o JPG)",
        "shot_button": "Revisar captura", "reading": "Leyendo la captura…",
        "examples": "Pruebe un ejemplo:", "checking": "Revisando el mensaje… puede tardar unos 20 segundos.",
        "empty": "Primero pegue un mensaje.",
        "stays": "Su mensaje se queda en su dispositivo.",
        "help": "¿Necesita ayuda para pegar un mensaje?",
        "help_body": "1. Abra el mensaje en su teléfono.\n\n2. Mantenga presionado el texto y toque **Copiar**.\n\n3. Vuelva aquí, mantenga presionado el cuadro y toque **Pegar**.\n\nO tome una captura de pantalla y súbala.",
        "bigger": "Letra más grande", "helper": "Una ayuda, no una garantía.",
        "result": "RESULTADO", "scam": "Estafa", "suspicious": "Sospechoso", "safe": "Parece seguro",
        "scam_meaning": "Es muy probable que sea una estafa. No toque enlaces, no responda y no pague.",
        "suspicious_meaning": "Algo no parece bien. No toque nada ni pague hasta confirmar con la organización real.",
        "safe_meaning": "No encontramos señales de alerta. Aun así, nunca comparta contraseñas ni códigos.",
        "noticed": "Lo que encontramos en el mensaje", "advice": "Qué significa",
        "todo": "Qué hacer ahora", "family": "Avisar a mi familia",
        "family_sub": "Un aviso seguro para pegar en el chat familiar. Nunca incluye el enlace de la estafa.",
        "read_aloud": "Escuchar", "ai_ready": "IA lista", "ai_off": "IA apagada · solo revisión automática",
        "extracted": "Texto leído de la captura",
        "disclaimer": "Si tiene dudas, contacte a la organización por su sitio web o teléfono oficial.",
    },
    "ar": {
        "headline": "لست متأكدًا من رسالة؟",
        "sub": "الصقها بالأسفل، وسنساعدك على فحصها.",
        "label": "الصق رسالتك أو بريدك هنا",
        "placeholder": "المس هنا والصق الرسالة التي وصلتك…",
        "check": "افحص الرسالة", "upload_link": "أو ارفع لقطة شاشة",
        "upload_label": "اختر لقطة شاشة للرسالة (PNG أو JPG)",
        "shot_button": "افحص اللقطة", "reading": "جارٍ قراءة اللقطة…",
        "examples": "جرّب مثالًا:", "checking": "جارٍ فحص الرسالة… قد يستغرق ذلك نحو 20 ثانية.",
        "empty": "الصق رسالة أولًا.",
        "stays": "رسالتك تبقى على جهازك.",
        "help": "تحتاج مساعدة في لصق رسالة؟",
        "help_body": "١. افتح الرسالة على هاتفك.\n\n٢. اضغط مطولًا على النص ثم اختر **نسخ**.\n\n٣. ارجع هنا، واضغط مطولًا على المربع ثم اختر **لصق**.\n\nأو التقط لقطة شاشة وارفعها.",
        "bigger": "تكبير الخط", "helper": "أداة مساعدة، وليست ضمانًا.",
        "result": "النتيجة", "scam": "احتيال", "suspicious": "مشبوه", "safe": "تبدو آمنة",
        "scam_meaning": "هذه على الأرجح عملية احتيال. لا تضغط على الروابط ولا ترد ولا تدفع.",
        "suspicious_meaning": "يبدو أن هناك شيئًا خاطئًا. لا تضغط ولا تدفع قبل التأكد من الجهة الحقيقية.",
        "safe_meaning": "لم نجد علامات تحذير. ومع ذلك، لا تشارك كلمات المرور أو الرموز أبدًا.",
        "noticed": "ما لاحظناه في الرسالة", "advice": "ماذا يعني هذا",
        "todo": "ماذا تفعل الآن", "family": "حذّر عائلتي",
        "family_sub": "تحذير آمن للصقه في مجموعة العائلة. لا يتضمن رابط الاحتيال أبدًا.",
        "read_aloud": "استمع", "ai_ready": "الذكاء الاصطناعي جاهز", "ai_off": "الذكاء الاصطناعي متوقف · فحص تلقائي فقط",
        "extracted": "النص المقروء من اللقطة",
        "disclaimer": "عند الشك، تواصل مع الجهة عبر موقعها أو رقمها الرسمي.",
    },
    "hi": {
        "headline": "किसी मैसेज पर शक है?",
        "sub": "उसे नीचे पेस्ट करें। हम जांचने में आपकी मदद करेंगे।",
        "label": "अपना मैसेज या ईमेल यहां पेस्ट करें",
        "placeholder": "यहां छुएं और मिला हुआ मैसेज पेस्ट करें…",
        "check": "मैसेज जांचें", "upload_link": "या स्क्रीनशॉट अपलोड करें",
        "upload_label": "मैसेज का स्क्रीनशॉट चुनें (PNG या JPG)",
        "shot_button": "स्क्रीनशॉट जांचें", "reading": "स्क्रीनशॉट पढ़ा जा रहा है…",
        "examples": "कोई उदाहरण आज़माएं:", "checking": "मैसेज जांचा जा रहा है… इसमें लगभग 20 सेकंड लग सकते हैं।",
        "empty": "पहले कोई मैसेज पेस्ट करें।",
        "stays": "आपका मैसेज आपके डिवाइस पर ही रहता है।",
        "help": "मैसेज पेस्ट करने में मदद चाहिए?",
        "help_body": "1. अपने फ़ोन पर मैसेज खोलें।\n\n2. टेक्स्ट को दबाकर रखें, फिर **कॉपी** पर टैप करें।\n\n3. यहां वापस आएं, बॉक्स को दबाकर रखें, फिर **पेस्ट** पर टैप करें।\n\nया स्क्रीनशॉट लेकर अपलोड करें।",
        "bigger": "टेक्स्ट बड़ा करें", "helper": "यह मदद है, गारंटी नहीं।",
        "result": "नतीजा", "scam": "धोखा", "suspicious": "संदिग्ध", "safe": "सुरक्षित लगता है",
        "scam_meaning": "यह लगभग पक्का धोखा है। लिंक पर क्लिक न करें, जवाब न दें और पैसे न भेजें।",
        "suspicious_meaning": "कुछ गड़बड़ लगती है। असली संस्था से पुष्टि किए बिना क्लिक न करें और पैसे न दें।",
        "safe_meaning": "हमें कोई खतरे का संकेत नहीं मिला। फिर भी कभी पासवर्ड या कोड किसी को न दें।",
        "noticed": "मैसेज में हमें क्या दिखा", "advice": "इसका मतलब",
        "todo": "अब क्या करें", "family": "परिवार को सावधान करें",
        "family_sub": "फ़ैमिली ग्रुप में भेजने के लिए सुरक्षित चेतावनी। इसमें धोखे वाला लिंक कभी नहीं होता।",
        "read_aloud": "सुनें", "ai_ready": "AI तैयार है", "ai_off": "AI बंद है · सिर्फ़ अपने-आप जांच",
        "extracted": "स्क्रीनशॉट से पढ़ा गया टेक्स्ट",
        "disclaimer": "शक हो तो संस्था की आधिकारिक वेबसाइट या फ़ोन नंबर से संपर्क करें।",
    },
    "fr": {
        "headline": "Un message vous semble louche ?",
        "sub": "Collez-le ci-dessous. Nous vous aidons à le vérifier.",
        "label": "Collez votre texto ou courriel ici",
        "placeholder": "Touchez ici et collez le message reçu…",
        "check": "Vérifier le message", "upload_link": "Ou téléversez une capture d'écran",
        "upload_label": "Choisissez une capture d'écran du message (PNG ou JPG)",
        "shot_button": "Vérifier la capture", "reading": "Lecture de la capture…",
        "examples": "Essayez un exemple :", "checking": "Vérification du message… cela peut prendre environ 20 secondes.",
        "empty": "Collez d'abord un message.",
        "stays": "Votre message reste sur votre appareil.",
        "help": "Besoin d'aide pour coller un message ?",
        "help_body": "1. Ouvrez le message sur votre téléphone.\n\n2. Appuyez longuement sur le texte, puis touchez **Copier**.\n\n3. Revenez ici, appuyez longuement sur la case, puis touchez **Coller**.\n\nOu prenez une capture d'écran et téléversez-la.",
        "bigger": "Agrandir le texte", "helper": "Une aide, pas une garantie.",
        "result": "RÉSULTAT", "scam": "Arnaque", "suspicious": "Suspect", "safe": "Semble sûr",
        "scam_meaning": "C'est très probablement une arnaque. Ne cliquez pas, ne répondez pas et ne payez pas.",
        "suspicious_meaning": "Quelque chose cloche. Ne cliquez pas et ne payez pas avant de vérifier auprès du vrai organisme.",
        "safe_meaning": "Nous n'avons trouvé aucun signal d'alerte. Ne partagez quand même jamais vos mots de passe ou codes.",
        "noticed": "Ce que nous avons remarqué", "advice": "Ce que ça veut dire",
        "todo": "Que faire maintenant", "family": "Avertir ma famille",
        "family_sub": "Un avertissement sûr à coller dans le groupe familial. Il n'inclut jamais le lien frauduleux.",
        "read_aloud": "Écouter", "ai_ready": "IA prête", "ai_off": "IA arrêtée · vérifications automatiques seulement",
        "extracted": "Texte lu dans la capture",
        "disclaimer": "En cas de doute, contactez l'organisme par son site ou son numéro officiel.",
    },
}

EXAMPLES = {
    "📦 Package fee": "Canada Post: Your package is on hold due to an unpaid shipping fee of $2.99. "
                     "Pay within 24 hours or it will be returned: http://canadapost-redelivery.info",
    "🏛️ CRA gift cards": "CRA: You owe $1,240 in unpaid taxes. Pay today with Google Play gift cards "
                        "or a warrant will be issued for your arrest. Call 1-888-555-0199.",
    "🏫 School reminder": "Reminder from Maple Grove Public School: Picture day is this Thursday. "
                         "Please send your child in their school uniform.",
}

VERDICT_STYLE = {  # card background, border, text, icon circle, icon
    "Scam": ("#FDECEA", "#E3A49D", "#8E1B13", "#B3261E", "!"),
    "Suspicious": ("#FFF4DB", "#E5C27A", "#6B4700", "#A86A00", "?"),
    "Safe": ("#E6F4EC", "#9CCFB1", "#135C35", "#1E7A47", "✓"),
}

# ---------------------------------------------------------------- startup helpers


@st.cache_resource
def _warm():
    return warm_up()  # load the model once so the first check is fast


_warm()


@st.cache_data(ttl=15)
def _model_ready():
    return is_model_ready()


@st.cache_data
def _img_b64(path):
    p = Path(path)
    return base64.b64encode(p.read_bytes()).decode() if p.exists() else ""


def block(s):
    """Strip indentation so Streamlit's markdown doesn't turn HTML into code blocks."""
    return "\n".join(line.strip() for line in s.splitlines() if line.strip())


def esc(x):
    return html.escape(str(x))


def highlight(text, phrases):
    """HTML-escape the message and wrap each suspicious phrase in <mark>."""
    lower = text.lower()
    spans = []
    for p in phrases:
        pl = p.lower()
        start = 0
        while pl and (i := lower.find(pl, start)) != -1:
            spans.append((i, i + len(p)))
            start = i + len(p)
    spans.sort()
    merged = []
    for s, e in spans:
        if merged and s <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], e))
        else:
            merged.append((s, e))
    out, pos = [], 0
    for s, e in merged:
        out.append(esc(text[pos:s]))
        out.append(f"<mark>{esc(text[s:e])}</mark>")
        pos = e
    out.append(esc(text[pos:]))
    return "".join(out).replace("\n", "<br>")


# ---------------------------------------------------------------- state

for key, default in {"msg": "", "show_upload": False, "bigger": False}.items():
    st.session_state.setdefault(key, default)


def use_example(text):
    st.session_state.msg = text
    st.session_state.pop("result", None)


def toggle_upload():
    st.session_state.show_upload = not st.session_state.show_upload


big = st.session_state.bigger
base = 21 if big else 18

# ---------------------------------------------------------------- style

st.markdown(block(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Lexend:wght@400;500;600;700;800&family=Noto+Nastaliq+Urdu:wght@400;700&family=Noto+Naskh+Arabic:wght@400;700&family=Noto+Sans+Devanagari:wght@400;600;700&display=swap');
:root {{ --ink:#0F1F3D; --muted:#4A5568; --teal:#0E6E74; --teal-dark:#0A5257; --cream:#FBF8F1; --line:#E6E1D6; }}
.stApp {{ background: var(--cream); }}
.stApp, .stApp p, .stApp li, .stApp label, .stApp textarea, .stApp button, .stApp input {{
  font-family: 'Lexend', 'Noto Sans Devanagari', system-ui, sans-serif; color: var(--ink); }}
.stApp p, .stApp li, .stApp textarea {{ font-size: {base}px; line-height: 1.6; }}
.block-container {{ max-width: 860px; padding-top: 1.2rem; padding-bottom: 3rem; }}
header[data-testid="stHeader"] {{ background: transparent; }}
textarea {{ unicode-bidi: plaintext; border-radius: 12px !important; font-size:{base}px !important; }}

.pg-brand {{ display:flex; align-items:center; gap:10px; font-weight:700; font-size:22px; color:var(--ink); margin-top:4px; }}
.pg-brand img {{ width:40px; height:auto; }}
.pg-hero {{ display:flex; align-items:center; gap:16px; margin:18px 0 10px; }}
.pg-hero-text {{ flex:1; min-width:0; }}
.pg-h1 {{ font-weight:800; font-size:{base + 28}px; line-height:1.1; letter-spacing:-1px; margin:0 0 8px; color:var(--ink); }}
.pg-sub {{ font-weight:500; font-size:{base + 6}px; line-height:1.35; margin:0; color:var(--ink); }}
.pg-mascot {{ flex:0 0 190px; max-width:32%; }}
.pg-mascot img {{ width:100%; height:auto; display:block; }}

.st-key-card {{ background:#FFFFFF; border-radius:18px; padding:24px 26px 18px; box-shadow:0 2px 10px rgba(15,31,61,.06), 0 1px 2px rgba(15,31,61,.05); border:1px solid var(--line); }}
.st-key-card label p {{ font-weight:600 !important; font-size:{base}px !important; }}
.stButton > button {{ border-radius:12px; min-height:46px; font-size:{base - 2}px; }}
.stButton > button[kind="primary"] {{ background:var(--teal); border:none; min-height:58px; font-weight:600; font-size:{base + 2}px; color:#FFF; }}
.stButton > button[kind="primary"]:hover {{ background:var(--teal-dark); color:#FFF; }}
.stButton > button[kind="tertiary"] {{ color:var(--teal); font-weight:600; min-height:44px; }}
button:focus-visible {{ outline:3px solid var(--teal) !important; outline-offset:2px; }}

.pg-stays {{ text-align:center; color:var(--muted); font-size:{base - 2}px; margin:14px 0 4px; }}
.pg-dot {{ display:inline-block; width:9px; height:9px; border-radius:50%; margin:0 6px 0 10px; vertical-align:middle; }}
.pg-section {{ margin-top:22px; }}
.pg-verdict {{ border-radius:18px; padding:22px 24px; display:flex; gap:18px; align-items:flex-start; border:2px solid; margin:6px 0 12px; }}
.pg-icon {{ flex:0 0 56px; height:56px; border-radius:50%; color:#FFF; font-size:30px; font-weight:700; display:flex; align-items:center; justify-content:center; }}
.pg-vlabel {{ font-size:14px; font-weight:700; letter-spacing:1.2px; }}
.pg-vword {{ font-weight:800; font-size:{base + 22}px; line-height:1.2; margin:2px 0 4px; }}
.pg-card {{ background:#FFF; border:1px solid var(--line); border-radius:18px; padding:20px 24px; margin-bottom:14px; }}
.pg-card h3 {{ font-weight:700; font-size:{base + 3}px; margin:0 0 10px; color:var(--ink); }}
.pg-msg {{ background:#F8F6F0; border-radius:12px; padding:14px 18px; line-height:1.75; font-size:{base}px; unicode-bidi:plaintext; }}
.pg-msg mark {{ background:#FFE08A; color:var(--ink); border-bottom:2px solid #9A6B00; padding:1px 3px; border-radius:3px; }}
.pg-advice {{ background:#FFF6E0; color:#4A3500; border-radius:12px; padding:12px 16px; margin-top:12px; font-size:{base}px; }}
.pg-steps {{ list-style:none; padding:0; margin:0; }}
.pg-steps li {{ display:flex; gap:12px; align-items:flex-start; margin-bottom:10px; }}
.pg-num {{ flex:0 0 30px; height:30px; border-radius:50%; background:var(--teal); color:#FFF; font-weight:700; font-size:16px; display:inline-flex; align-items:center; justify-content:center; }}
.pg-foot {{ display:flex; justify-content:space-between; gap:12px; flex-wrap:wrap; color:var(--muted); font-size:14px; margin-top:28px; border-top:1px solid var(--line); padding-top:12px; }}

.pg-rtl {{ direction:rtl; text-align:right; }}
.pg-rtl.ur, .pg-rtl.ur p, .pg-rtl.ur li, .pg-rtl.ur h3, .pg-rtl.ur .pg-h1, .pg-rtl.ur .pg-sub, .pg-rtl.ur .pg-vword {{ font-family:'Noto Nastaliq Urdu',serif; line-height:2.1; letter-spacing:0; }}
.pg-rtl.ar, .pg-rtl.ar p, .pg-rtl.ar li, .pg-rtl.ar h3, .pg-rtl.ar .pg-h1, .pg-rtl.ar .pg-sub, .pg-rtl.ar .pg-vword {{ font-family:'Noto Naskh Arabic',serif; line-height:1.7; letter-spacing:0; }}
.pg-rtl .pg-msg {{ direction:ltr; text-align:left; font-family:'Lexend',sans-serif; line-height:1.75; }}
@media (max-width: 640px) {{ .pg-mascot {{ flex-basis:120px; }} .pg-h1 {{ font-size:{base + 16}px; }} .pg-sub {{ font-size:{base + 2}px; }} }}
</style>
"""), unsafe_allow_html=True)

# ---------------------------------------------------------------- header: logo + language

hl, hr = st.columns([3, 1.3], vertical_alignment="center")
with hr:
    lang_label = st.selectbox("Language", list(LANG_OPTIONS), index=0,
                              format_func=lambda x: f"🌐  {x}", label_visibility="collapsed")
lang = LANG_OPTIONS[lang_label]
t = UI[lang]
rtl = f" pg-rtl {lang}" if lang in RTL else ""
with hl:
    icon_b64 = _img_b64(str(ICON))
    logo = f'<img src="data:image/png;base64,{icon_b64}" alt="">' if icon_b64 else ""
    st.markdown(f'<div class="pg-brand">{logo}<span>PhishGuard</span></div>', unsafe_allow_html=True)

# ---------------------------------------------------------------- hero

mascot_b64 = _img_b64(str(MASCOT))
mascot = (f'<div class="pg-mascot"><img src="data:image/png;base64,{mascot_b64}" '
          f'alt="PhishGuard mascot: a goldfish in knight armour holding a shield"></div>') if mascot_b64 else ""
st.markdown(block(f"""
<div class="pg-hero{rtl}">
<div class="pg-hero-text"><h1 class="pg-h1">{esc(t["headline"])}</h1><p class="pg-sub">{esc(t["sub"])}</p></div>
{mascot}
</div>
"""), unsafe_allow_html=True)

# ---------------------------------------------------------------- input card

with st.container(key="card"):
    st.text_area(t["label"], key="msg", height=150, placeholder=t["placeholder"])

    if st.button(t["check"], type="primary", use_container_width=True, icon=":material/verified_user:"):
        if not st.session_state.msg.strip():
            st.warning(t["empty"])
        else:
            with st.spinner(t["checking"]):
                st.session_state.result = check_message(st.session_state.msg, lang)
                st.session_state.result_text = st.session_state.msg
                st.session_state.result_lang = lang

    st.button(t["upload_link"], type="tertiary", icon=":material/upload:",
              on_click=toggle_upload, use_container_width=True)
    if st.session_state.show_upload:
        shot = st.file_uploader(t["upload_label"], type=["png", "jpg", "jpeg"])
        if shot is not None:
            st.image(shot, use_container_width=True)
            if st.button(t["shot_button"], type="primary", use_container_width=True, icon=":material/image_search:"):
                with st.spinner(t["reading"]):
                    res = check_image(shot.getvalue(), lang)
                st.session_state.result = res
                st.session_state.result_text = res.get("extracted_text", "")
                st.session_state.result_lang = lang

    st.caption(t["examples"])
    ex_cols = st.columns(len(EXAMPLES))
    for col, (name, example) in zip(ex_cols, EXAMPLES.items()):
        col.button(name, on_click=use_example, args=(example,), use_container_width=True)

# privacy line + AI status
ready = _model_ready()
dot = ('<span class="pg-dot" style="background:#1E7A47"></span>' + esc(t["ai_ready"])) if ready else \
      ('<span class="pg-dot" style="background:#A86A00"></span>' + esc(t["ai_off"]))
st.markdown(f'<p class="pg-stays{rtl}">🔒 {esc(t["stays"])} {dot}</p>', unsafe_allow_html=True)

# help + bigger text
c1, c2 = st.columns(2)
with c1:
    with st.popover(t["help"], icon=":material/help:", use_container_width=True):
        st.markdown(t["help_body"])
with c2:
    st.toggle(f'Aa  {t["bigger"]}', key="bigger")

# ---------------------------------------------------------------- result

result = st.session_state.get("result")
if result:
    r_lang = st.session_state.get("result_lang", lang)
    rt = UI[r_lang]
    r_rtl = f" pg-rtl {r_lang}" if r_lang in RTL else ""
    st.markdown('<div class="pg-section"></div>', unsafe_allow_html=True)

    if not result.get("ok"):
        st.error(result.get("error") or "Something went wrong. Please try again.")
    else:
        verdict = result["verdict"]
        bg, border, fg, circle, icon = VERDICT_STYLE[verdict]
        meaning = rt[f"{verdict.lower()}_meaning"]

        if result.get("warning"):
            st.warning(result["warning"])

        # Verdict card
        st.markdown(block(f"""
        <div class="pg-verdict{r_rtl}" style="background:{bg};border-color:{border};color:{fg}" role="status">
        <div class="pg-icon" style="background:{circle}" aria-hidden="true">{icon}</div>
        <div style="flex:1;min-width:0">
        <div class="pg-vlabel">{esc(rt["result"])}</div>
        <div class="pg-vword">{esc(rt[verdict.lower()])}</div>
        <p style="margin:0;color:{fg}">{esc(meaning)}</p>
        </div></div>
        """), unsafe_allow_html=True)

        # Read aloud (the browser's own voice, so it stays on the device)
        speech = " ".join([rt[verdict.lower()], meaning, result.get("advice", "")] + result.get("red_flags", []))
        read_aloud_html = f"""
        <button id="say" style="font:600 16px Lexend,system-ui,sans-serif;min-height:46px;padding:8px 18px;border-radius:12px;
        border:1.5px solid #0E6E74;background:#fff;color:#0E6E74;cursor:pointer">🔊 {esc(rt["read_aloud"])}</button>
        <script>
        document.getElementById('say').onclick = () => {{
          const u = new SpeechSynthesisUtterance({json.dumps(speech)});
          u.lang = {json.dumps(SPEECH_LANG.get(r_lang, "en-CA"))}; u.rate = 0.9;
          speechSynthesis.cancel(); speechSynthesis.speak(u);
        }};
        </script>"""
        try:  # optional: skip quietly if this Streamlit version dropped components.html
            components.html(read_aloud_html, height=58)
        except Exception:
            pass

        # What we noticed: highlighted message + red flags + advice
        msg_text = st.session_state.get("result_text", "")
        extracted = ""
        if result.get("extracted_text"):
            extracted = f'<p style="font-size:15px;color:#4A5568;margin:0 0 6px">{esc(rt["extracted"])}</p>'
        flags = "".join(f"<li>{esc(f)}</li>" for f in result.get("red_flags", []))
        st.markdown(block(f"""
        <div class="pg-card{r_rtl}">
        <h3>{esc(rt["noticed"])}</h3>
        {extracted}
        <div class="pg-msg">{highlight(msg_text, result.get("highlights", []))}</div>
        {f'<ul style="margin:12px 0 0">{flags}</ul>' if flags else ''}
        <div class="pg-advice"><strong>{esc(rt["advice"])}:</strong> {esc(result.get("advice", ""))}</div>
        </div>
        """), unsafe_allow_html=True)

        # What to do now (fixed text, never AI-generated)
        steps = ACTION_STEPS.get(r_lang, ACTION_STEPS["en"])
        steps_html = "".join(f'<li><span class="pg-num">{i}</span><span>{esc(s)}</span></li>'
                             for i, s in enumerate(steps, 1))
        st.markdown(block(f"""
        <div class="pg-card{r_rtl}">
        <h3>{esc(rt["todo"])}</h3>
        <ol class="pg-steps">{steps_html}</ol>
        </div>
        """), unsafe_allow_html=True)

        # Warn my family (copy button built into st.code)
        if verdict != "Safe" and result.get("family_warning"):
            st.markdown(block(f"""
            <div class="pg-card{r_rtl}" style="margin-bottom:6px">
            <h3>{esc(rt["family"])}</h3>
            <p style="margin:0;font-size:16px;color:#4A5568">{esc(rt["family_sub"])}</p>
            </div>
            """), unsafe_allow_html=True)
            try:
                st.code(result["family_warning"], language=None, wrap_lines=True)
            except TypeError:  # older Streamlit without wrap_lines
                st.code(result["family_warning"], language=None)

# ---------------------------------------------------------------- footer + sidebar

st.markdown(block(f"""
<div class="pg-foot{rtl}">
<span>{esc(t["helper"])} {esc(t["disclaimer"])}</span>
<span>Gemma 3 4B · open-weight · MIT</span>
</div>
"""), unsafe_allow_html=True)

with st.sidebar:
    if MASCOT.exists():
        st.image(str(MASCOT), width=140)
    st.markdown("### About PhishGuard")
    st.write("PhishGuard helps families spot scam texts and emails, in their own language. "
             "Rule checks plus a local open-weight AI model. Nothing is sent online.")
    st.markdown(f"**Model:** Gemma 3 4B (`{MODEL}`), run locally with Ollama")
    st.markdown("[Gemma terms of use](https://ai.google.dev/gemma/terms)")
    st.caption(PRIVACY_NOTE.get(lang, PRIVACY_NOTE["en"]))
    st.caption("Built at Hacktoberfest x ElleHacks Hack Day 2026 · MIT License")
