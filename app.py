"""
app.py - Hoshiyar: the scam checker web app (Streamlit).

Run:  streamlit run app.py      (opens at http://localhost:8501)

Uses checker.py (rules + local Gemma 3 4B) and resources.py (fixed "what to do" text).
"""

import html
import json

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

st.set_page_config(page_title="Hoshiyar", page_icon="🛡️", layout="wide")

# ---------------------------------------------------------------- languages

LANG_OPTIONS = {  # label shown -> code used by checker.py
    "English": "en", "اردو": "ur", "Español": "es",
    "العربية": "ar", "हिन्दी": "hi", "Français": "fr",
}
RTL = {"ur", "ar"}
SPEECH_LANG = {"en": "en-CA", "ur": "ur-PK", "es": "es-ES", "ar": "ar-SA", "hi": "hi-IN", "fr": "fr-CA"}

UI = {
    "en": {
        "tagline": "Check a message before you trust it",
        "label": "Paste the text or email you received",
        "placeholder": "Paste the whole message here, including any links…",
        "examples": "Try an example:", "check": "Check message",
        "tab_paste": "Paste text", "tab_shot": "Upload a screenshot",
        "upload_label": "Choose a screenshot of the message (PNG or JPG)",
        "shot_button": "Check screenshot", "reading": "Reading the screenshot…",
        "checking": "Checking the message…", "empty": "Please paste a message first.",
        "result": "RESULT", "scam": "Scam", "suspicious": "Suspicious", "safe": "Looks safe",
        "scam_meaning": "This is very likely a scam. Don't click links, reply, or pay.",
        "suspicious_meaning": "Something looks wrong. Don't click or pay until you check with the real organization.",
        "safe_meaning": "We didn't find warning signs. Still, never share passwords or codes.",
        "noticed": "What we noticed in the message", "advice": "What this means",
        "todo": "What to do now", "family": "Warn my family",
        "family_sub": "A safe warning to paste in your family chat. It never includes the scam link.",
        "read_aloud": "Read aloud", "ai_ready": "AI ready · on this laptop",
        "ai_off": "AI not running · rule checks only", "easy": "Easy mode (bigger text)",
        "disclaimer": "This is a helper, not a guarantee. When in doubt, contact the organization using its official website or phone number.",
        "extracted": "Text we read from the screenshot", "language": "Language",
    },
    "ur": {
        "tagline": "کسی پیغام پر بھروسہ کرنے سے پہلے اسے چیک کریں",
        "label": "جو پیغام یا ای میل آپ کو ملی ہے، یہاں پیسٹ کریں",
        "placeholder": "پورا پیغام یہاں پیسٹ کریں، لنک سمیت…",
        "examples": "مثال آزمائیں:", "check": "پیغام چیک کریں",
        "tab_paste": "پیغام پیسٹ کریں", "tab_shot": "اسکرین شاٹ اپ لوڈ کریں",
        "upload_label": "پیغام کا اسکرین شاٹ منتخب کریں (PNG یا JPG)",
        "shot_button": "اسکرین شاٹ چیک کریں", "reading": "اسکرین شاٹ پڑھا جا رہا ہے…",
        "checking": "پیغام چیک کیا جا رہا ہے…", "empty": "پہلے کوئی پیغام پیسٹ کریں۔",
        "result": "نتیجہ", "scam": "فراڈ", "suspicious": "مشکوک", "safe": "محفوظ لگتا ہے",
        "scam_meaning": "یہ تقریباً یقینی طور پر فراڈ ہے۔ لنک پر کلک نہ کریں، جواب نہ دیں اور پیسے نہ بھیجیں۔",
        "suspicious_meaning": "کچھ گڑبڑ لگتی ہے۔ اصل ادارے سے تصدیق کیے بغیر کلک نہ کریں اور پیسے نہ دیں۔",
        "safe_meaning": "ہمیں خطرے کی کوئی نشانی نہیں ملی۔ پھر بھی کبھی پاس ورڈ یا کوڈ کسی کو نہ دیں۔",
        "noticed": "پیغام میں ہمیں کیا نظر آیا", "advice": "اس کا مطلب",
        "todo": "اب کیا کریں", "family": "گھر والوں کو خبردار کریں",
        "family_sub": "فیملی گروپ میں بھیجنے کے لیے محفوظ پیغام۔ اس میں فراڈ والا لنک کبھی شامل نہیں ہوتا۔",
        "read_aloud": "سنیں", "ai_ready": "AI تیار ہے · اسی لیپ ٹاپ پر",
        "ai_off": "AI بند ہے · صرف خودکار جانچ", "easy": "آسان موڈ (بڑا متن)",
        "disclaimer": "یہ صرف مدد کے لیے ہے، گارنٹی نہیں۔ شک ہو تو ادارے سے اس کی سرکاری ویب سائٹ یا فون نمبر کے ذریعے رابطہ کریں۔",
        "extracted": "اسکرین شاٹ سے پڑھا گیا متن", "language": "زبان",
    },
    "es": {
        "tagline": "Revise un mensaje antes de confiar en él",
        "label": "Pegue el mensaje de texto o correo que recibió",
        "placeholder": "Pegue aquí el mensaje completo, con los enlaces…",
        "examples": "Pruebe un ejemplo:", "check": "Revisar mensaje",
        "tab_paste": "Pegar texto", "tab_shot": "Subir captura de pantalla",
        "upload_label": "Elija una captura de pantalla del mensaje (PNG o JPG)",
        "shot_button": "Revisar captura", "reading": "Leyendo la captura…",
        "checking": "Revisando el mensaje…", "empty": "Primero pegue un mensaje.",
        "result": "RESULTADO", "scam": "Estafa", "suspicious": "Sospechoso", "safe": "Parece seguro",
        "scam_meaning": "Es muy probable que sea una estafa. No toque enlaces, no responda y no pague.",
        "suspicious_meaning": "Algo no parece bien. No toque nada ni pague hasta confirmar con la organización real.",
        "safe_meaning": "No encontramos señales de alerta. Aun así, nunca comparta contraseñas ni códigos.",
        "noticed": "Lo que encontramos en el mensaje", "advice": "Qué significa",
        "todo": "Qué hacer ahora", "family": "Avisar a mi familia",
        "family_sub": "Un aviso seguro para pegar en el chat familiar. Nunca incluye el enlace de la estafa.",
        "read_aloud": "Escuchar", "ai_ready": "IA lista · en esta computadora",
        "ai_off": "IA apagada · solo revisión automática", "easy": "Modo fácil (texto más grande)",
        "disclaimer": "Es una ayuda, no una garantía. Si tiene dudas, contacte a la organización por su sitio web o teléfono oficial.",
        "extracted": "Texto leído de la captura", "language": "Idioma",
    },
    "ar": {
        "tagline": "افحص الرسالة قبل أن تثق بها",
        "label": "الصق الرسالة النصية أو البريد الذي وصلك",
        "placeholder": "الصق الرسالة كاملة هنا مع أي روابط…",
        "examples": "جرّب مثالًا:", "check": "افحص الرسالة",
        "tab_paste": "لصق النص", "tab_shot": "رفع لقطة شاشة",
        "upload_label": "اختر لقطة شاشة للرسالة (PNG أو JPG)",
        "shot_button": "افحص اللقطة", "reading": "جارٍ قراءة اللقطة…",
        "checking": "جارٍ فحص الرسالة…", "empty": "الصق رسالة أولًا.",
        "result": "النتيجة", "scam": "احتيال", "suspicious": "مشبوه", "safe": "تبدو آمنة",
        "scam_meaning": "هذه على الأرجح عملية احتيال. لا تضغط على الروابط ولا ترد ولا تدفع.",
        "suspicious_meaning": "يبدو أن هناك شيئًا خاطئًا. لا تضغط ولا تدفع قبل التأكد من الجهة الحقيقية.",
        "safe_meaning": "لم نجد علامات تحذير. ومع ذلك، لا تشارك كلمات المرور أو الرموز أبدًا.",
        "noticed": "ما لاحظناه في الرسالة", "advice": "ماذا يعني هذا",
        "todo": "ماذا تفعل الآن", "family": "حذّر عائلتي",
        "family_sub": "تحذير آمن للصقه في مجموعة العائلة. لا يتضمن رابط الاحتيال أبدًا.",
        "read_aloud": "استمع", "ai_ready": "الذكاء الاصطناعي جاهز · على هذا الجهاز",
        "ai_off": "الذكاء الاصطناعي متوقف · فحص تلقائي فقط", "easy": "الوضع السهل (خط أكبر)",
        "disclaimer": "هذه أداة مساعدة وليست ضمانًا. عند الشك، تواصل مع الجهة عبر موقعها أو رقمها الرسمي.",
        "extracted": "النص المقروء من اللقطة", "language": "اللغة",
    },
    "hi": {
        "tagline": "किसी मैसेज पर भरोसा करने से पहले उसे जांचें",
        "label": "जो मैसेज या ईमेल आपको मिला है, उसे यहां पेस्ट करें",
        "placeholder": "पूरा मैसेज यहां पेस्ट करें, लिंक के साथ…",
        "examples": "कोई उदाहरण आज़माएं:", "check": "मैसेज जांचें",
        "tab_paste": "टेक्स्ट पेस्ट करें", "tab_shot": "स्क्रीनशॉट अपलोड करें",
        "upload_label": "मैसेज का स्क्रीनशॉट चुनें (PNG या JPG)",
        "shot_button": "स्क्रीनशॉट जांचें", "reading": "स्क्रीनशॉट पढ़ा जा रहा है…",
        "checking": "मैसेज जांचा जा रहा है…", "empty": "पहले कोई मैसेज पेस्ट करें।",
        "result": "नतीजा", "scam": "धोखा", "suspicious": "संदिग्ध", "safe": "सुरक्षित लगता है",
        "scam_meaning": "यह लगभग पक्का धोखा है। लिंक पर क्लिक न करें, जवाब न दें और पैसे न भेजें।",
        "suspicious_meaning": "कुछ गड़बड़ लगती है। असली संस्था से पुष्टि किए बिना क्लिक न करें और पैसे न दें।",
        "safe_meaning": "हमें कोई खतरे का संकेत नहीं मिला। फिर भी कभी पासवर्ड या कोड किसी को न दें।",
        "noticed": "मैसेज में हमें क्या दिखा", "advice": "इसका मतलब",
        "todo": "अब क्या करें", "family": "परिवार को सावधान करें",
        "family_sub": "फ़ैमिली ग्रुप में भेजने के लिए सुरक्षित चेतावनी। इसमें धोखे वाला लिंक कभी नहीं होता।",
        "read_aloud": "सुनें", "ai_ready": "AI तैयार है · इसी लैपटॉप पर",
        "ai_off": "AI बंद है · सिर्फ़ अपने-आप जांच", "easy": "आसान मोड (बड़ा टेक्स्ट)",
        "disclaimer": "यह सिर्फ़ मदद है, गारंटी नहीं। शक हो तो संस्था की आधिकारिक वेबसाइट या फ़ोन नंबर से संपर्क करें।",
        "extracted": "स्क्रीनशॉट से पढ़ा गया टेक्स्ट", "language": "भाषा",
    },
    "fr": {
        "tagline": "Vérifiez un message avant de lui faire confiance",
        "label": "Collez le texto ou le courriel reçu",
        "placeholder": "Collez le message complet ici, avec les liens…",
        "examples": "Essayez un exemple :", "check": "Vérifier le message",
        "tab_paste": "Coller le texte", "tab_shot": "Téléverser une capture d'écran",
        "upload_label": "Choisissez une capture d'écran du message (PNG ou JPG)",
        "shot_button": "Vérifier la capture", "reading": "Lecture de la capture…",
        "checking": "Vérification du message…", "empty": "Collez d'abord un message.",
        "result": "RÉSULTAT", "scam": "Arnaque", "suspicious": "Suspect", "safe": "Semble sûr",
        "scam_meaning": "C'est très probablement une arnaque. Ne cliquez pas, ne répondez pas et ne payez pas.",
        "suspicious_meaning": "Quelque chose cloche. Ne cliquez pas et ne payez pas avant de vérifier auprès du vrai organisme.",
        "safe_meaning": "Nous n'avons trouvé aucun signal d'alerte. Ne partagez quand même jamais vos mots de passe ou codes.",
        "noticed": "Ce que nous avons remarqué", "advice": "Ce que ça veut dire",
        "todo": "Que faire maintenant", "family": "Avertir ma famille",
        "family_sub": "Un avertissement sûr à coller dans le groupe familial. Il n'inclut jamais le lien frauduleux.",
        "read_aloud": "Écouter", "ai_ready": "IA prête · sur cet ordinateur",
        "ai_off": "IA arrêtée · vérifications automatiques seulement", "easy": "Mode facile (texte plus grand)",
        "disclaimer": "C'est une aide, pas une garantie. En cas de doute, contactez l'organisme par son site ou son numéro officiel.",
        "extracted": "Texte lu dans la capture", "language": "Langue",
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

VERDICT_STYLE = {  # card background, border, text, icon circle
    "Scam": ("#FDECEA", "#E3A49D", "#8E1B13", "#B3261E", "!"),
    "Suspicious": ("#FFF4DB", "#E5C27A", "#6B4700", "#A86A00", "?"),
    "Safe": ("#E6F4EC", "#9CCFB1", "#135C35", "#1E7A47", "✓"),
}

# ---------------------------------------------------------------- startup


@st.cache_resource
def _warm():
    return warm_up()  # load the model once so the first check is fast


_warm()


@st.cache_data(ttl=15)
def _model_ready():
    return is_model_ready()


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


# ---------------------------------------------------------------- sidebar + header controls

with st.sidebar:
    easy = st.toggle("Aa  Easy mode / آسان موڈ", value=False)
    st.markdown("### About")
    st.write("Hoshiyar helps families spot scam texts and emails, in their own language. "
             "Rule checks plus a local open-weight AI model. Nothing is sent online.")
    st.markdown(f"**Model:** Gemma 3 4B (`{MODEL}`), run locally with Ollama")
    st.markdown("[Gemma terms of use](https://ai.google.dev/gemma/terms)")
    st.caption("Built at Hacktoberfest x ElleHacks Hack Day 2026 · MIT License")

base = 21 if easy else 18

# ---------------------------------------------------------------- style

st.markdown(block(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:wght@400;700&family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,800&family=Noto+Nastaliq+Urdu:wght@400;700&family=Noto+Naskh+Arabic:wght@400;700&display=swap');
.stApp {{ background: #F3F5F4; }}
.stApp, .stApp p, .stApp li, .stApp label, .stApp textarea, .stApp button {{
  font-family: 'Atkinson Hyperlegible', system-ui, sans-serif; color: #16232B; }}
.stApp p, .stApp li, .stApp textarea {{ font-size: {base}px; line-height: 1.6; }}
.stApp label p {{ font-size: {base}px !important; font-weight: 700; }}
.block-container {{ max-width: 1200px; padding-top: 1.6rem; }}
textarea {{ unicode-bidi: plaintext; border-radius: 14px !important; }}
.hz-head {{ display:flex; align-items:center; gap:14px; }}
.hz-title {{ font-family:'Bricolage Grotesque',sans-serif; font-weight:800; font-size:34px; letter-spacing:-.5px; line-height:1.1; margin:0; }}
.hz-tag {{ font-size:16px; color:#4B5A63; margin:0; }}
.hz-pill {{ display:inline-flex; align-items:center; gap:8px; font-size:15px; padding:6px 14px; border-radius:999px; }}
.hz-dot {{ width:9px; height:9px; border-radius:50%; display:inline-block; }}
.hz-privacy {{ background:#E3EFEE; color:#0A474D; padding:12px 18px; border-radius:14px; font-size:{base - 1}px; margin:8px 0 18px; }}
.hz-card {{ background:#FFFFFF; border:1px solid #D9E0DE; border-radius:20px; padding:22px 26px; margin-bottom:16px; }}
.hz-card h3 {{ font-family:'Bricolage Grotesque',sans-serif; font-weight:600; font-size:22px; margin:0 0 10px; }}
.hz-verdict {{ border-radius:20px; padding:22px 26px; margin-bottom:16px; display:flex; gap:18px; align-items:flex-start; border-width:2px; border-style:solid; }}
.hz-icon {{ flex:0 0 56px; height:56px; border-radius:50%; color:#FFFFFF; font-size:30px; font-weight:700; display:flex; align-items:center; justify-content:center; }}
.hz-vlabel {{ font-size:14px; font-weight:700; letter-spacing:1.2px; }}
.hz-vword {{ font-family:'Bricolage Grotesque','Noto Nastaliq Urdu','Noto Naskh Arabic',sans-serif; font-weight:800; font-size:{base + 24}px; line-height:1.2; margin:2px 0 4px; }}
.hz-msg {{ background:#F7F9F8; border-radius:12px; padding:14px 18px; line-height:1.75; font-size:{base}px; unicode-bidi:plaintext; }}
.hz-msg mark {{ background:#FFE08A; color:#16232B; border-bottom:2px solid #9A6B00; padding:1px 3px; border-radius:3px; }}
.hz-advice {{ background:#FFF6E0; color:#4A3500; border-radius:12px; padding:12px 16px; margin-top:12px; font-size:{base}px; }}
.hz-steps {{ list-style:none; padding:0; margin:0; }}
.hz-steps li {{ display:flex; gap:12px; align-items:flex-start; margin-bottom:10px; }}
.hz-num {{ flex:0 0 30px; height:30px; border-radius:50%; background:#0E5E66; color:#FFF; font-weight:700; font-size:16px; display:inline-flex; align-items:center; justify-content:center; }}
.hz-foot {{ font-size:15px; color:#4B5A63; border-top:1px solid #D9E0DE; padding-top:14px; margin-top:10px; }}
.hz-rtl {{ direction:rtl; text-align:right; }}
.hz-rtl.ur, .hz-rtl.ur p, .hz-rtl.ur li {{ font-family:'Noto Nastaliq Urdu',serif; line-height:2.2; }}
.hz-rtl.ar, .hz-rtl.ar p, .hz-rtl.ar li {{ font-family:'Noto Naskh Arabic',serif; line-height:1.9; }}
.hz-rtl .hz-msg {{ direction:ltr; text-align:left; font-family:'Atkinson Hyperlegible',sans-serif; line-height:1.75; }}
div.stButton > button {{ min-height:48px; border-radius:12px; font-size:{base - 2}px; }}
div.stButton > button[kind="primary"] {{ background:#0E5E66; border:none; min-height:56px; font-weight:700; font-size:{base + 1}px; }}
div.stButton > button[kind="primary"]:hover {{ background:#0A474D; }}
button:focus-visible {{ outline:3px solid #0E5E66 !important; outline-offset:2px; }}
</style>
"""), unsafe_allow_html=True)

# ---------------------------------------------------------------- header

head_left, head_right = st.columns([3, 2])
with head_right:
    lang_label = st.selectbox("Language / زبان / Idioma", list(LANG_OPTIONS), index=0)
lang = LANG_OPTIONS[lang_label]
t = UI[lang]
rtl_cls = f" hz-rtl {lang}" if lang in RTL else ""
ready = _model_ready()

with head_left:
    pill = (f'<span class="hz-pill" style="background:#E6F4EC;color:#135C35"><span class="hz-dot" style="background:#1E7A47"></span>{esc(t["ai_ready"])}</span>'
            if ready else
            f'<span class="hz-pill" style="background:#FFF4DB;color:#6B4700"><span class="hz-dot" style="background:#A86A00"></span>{esc(t["ai_off"])}</span>')
    st.markdown(block(f"""
    <div class="hz-head">
    <svg width="48" height="48" viewBox="0 0 40 40" aria-hidden="true"><rect width="40" height="40" rx="11" fill="#0E5E66"></rect><path d="M8 20c3.5-6 8-9 12-9s8.5 3 12 9c-3.5 6-8 9-12 9s-8.5-3-12-9z" fill="none" stroke="#FFFFFF" stroke-width="2.4" stroke-linejoin="round"></path><circle cx="20" cy="20" r="4.2" fill="#FFE08A"></circle></svg>
    <div><p class="hz-title">Hoshiyar · ہوشیار</p><p class="hz-tag{rtl_cls}">{esc(t["tagline"])}</p></div>
    </div>
    <div style="margin-top:8px">{pill}</div>
    """), unsafe_allow_html=True)

st.markdown(f'<div class="hz-privacy{rtl_cls}">🔒 {esc(PRIVACY_NOTE.get(lang, PRIVACY_NOTE["en"]))}</div>',
            unsafe_allow_html=True)

# ---------------------------------------------------------------- input (left) / result (right)

if "msg" not in st.session_state:
    st.session_state.msg = ""


def use_example(text):
    st.session_state.msg = text
    st.session_state.pop("result", None)


left, right = st.columns([1, 1.25], gap="large")

with left:
    tab_paste, tab_shot = st.tabs([t["tab_paste"], t["tab_shot"]])

    with tab_paste:
        st.text_area(t["label"], key="msg", height=190, placeholder=t["placeholder"])
        st.caption(t["examples"])
        ex_cols = st.columns(len(EXAMPLES))
        for col, (name, example) in zip(ex_cols, EXAMPLES.items()):
            col.button(name, on_click=use_example, args=(example,), use_container_width=True)
        if st.button(t["check"], type="primary", use_container_width=True):
            if not st.session_state.msg.strip():
                st.warning(t["empty"])
            else:
                with st.spinner(t["checking"]):
                    st.session_state.result = check_message(st.session_state.msg, lang)
                    st.session_state.result_text = st.session_state.msg
                    st.session_state.result_lang = lang

    with tab_shot:
        shot = st.file_uploader(t["upload_label"], type=["png", "jpg", "jpeg"])
        if shot is not None:
            st.image(shot, use_container_width=True)
            if st.button(t["shot_button"], type="primary", use_container_width=True):
                with st.spinner(t["reading"]):
                    res = check_image(shot.getvalue(), lang)
                st.session_state.result = res
                st.session_state.result_text = res.get("extracted_text", "")
                st.session_state.result_lang = lang

with right:
    result = st.session_state.get("result")
    if result:
        r_lang = st.session_state.get("result_lang", lang)
        rt = UI[r_lang]
        r_rtl = f" hz-rtl {r_lang}" if r_lang in RTL else ""

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
            <div class="hz-verdict{r_rtl}" style="background:{bg};border-color:{border};color:{fg}">
            <div class="hz-icon" style="background:{circle}" aria-hidden="true">{icon}</div>
            <div style="flex:1;min-width:0">
            <div class="hz-vlabel">{esc(rt["result"])}</div>
            <div class="hz-vword">{esc(rt[verdict.lower()])}</div>
            <p style="margin:0;color:{fg}">{esc(meaning)}</p>
            </div></div>
            """), unsafe_allow_html=True)

            # Read aloud (browser voice, stays on the laptop)
            speech = " ".join([rt[verdict.lower()], meaning, result.get("advice", "")] + result.get("red_flags", []))
            read_aloud_html = f"""
            <button id="say" style="font:600 16px system-ui,sans-serif;min-height:46px;padding:8px 18px;border-radius:12px;
            border:1.5px solid #0E5E66;background:#fff;color:#0E5E66;cursor:pointer">🔊 {esc(rt["read_aloud"])}</button>
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
                extracted = f'<p style="font-size:15px;color:#4B5A63;margin:0 0 6px">{esc(rt["extracted"])}</p>'
            flags = "".join(f"<li>{esc(f)}</li>" for f in result.get("red_flags", []))
            st.markdown(block(f"""
            <div class="hz-card{r_rtl}">
            <h3>{esc(rt["noticed"])}</h3>
            {extracted}
            <div class="hz-msg">{highlight(msg_text, result.get("highlights", []))}</div>
            {f'<ul style="margin:12px 0 0">{flags}</ul>' if flags else ''}
            <div class="hz-advice"><strong>{esc(rt["advice"])}:</strong> {esc(result.get("advice", ""))}</div>
            </div>
            """), unsafe_allow_html=True)

            # What to do now (fixed, never AI-generated)
            steps = ACTION_STEPS.get(r_lang, ACTION_STEPS["en"])
            steps_html = "".join(f'<li><span class="hz-num">{i}</span><span>{esc(s)}</span></li>'
                                 for i, s in enumerate(steps, 1))
            st.markdown(block(f"""
            <div class="hz-card{r_rtl}">
            <h3>{esc(rt["todo"])}</h3>
            <ol class="hz-steps">{steps_html}</ol>
            </div>
            """), unsafe_allow_html=True)

            # Warn my family (copy button built into st.code)
            if verdict != "Safe" and result.get("family_warning"):
                st.markdown(block(f"""
                <div class="hz-card{r_rtl}" style="margin-bottom:6px">
                <h3>{esc(rt["family"])}</h3>
                <p style="margin:0;font-size:16px;color:#4B5A63">{esc(rt["family_sub"])}</p>
                </div>
                """), unsafe_allow_html=True)
                try:
                    st.code(result["family_warning"], language=None, wrap_lines=True)
                except TypeError:  # older Streamlit without wrap_lines
                    st.code(result["family_warning"], language=None)

st.markdown(f'<div class="hz-foot{rtl_cls}">{esc(t["disclaimer"])}</div>', unsafe_allow_html=True)
