"""
resources.py - owned by Person 1 (AI & prompt lead).

Fixed text shown on every result, in every language in prompts.LANGUAGES.
Numbers stay as digits in every language.
"""

ACTION_STEPS = {
    "en": [
        "Don't click links, reply, or pay.",
        "Forward scam texts to 7726 (SPAM).",
        "Report it to the Canadian Anti-Fraud Centre: 1-888-495-8501.",
        "Call your bank using the number on the back of your card.",
    ],
    "ur": [
        "کسی لنک پر کلک نہ کریں، جواب نہ دیں اور کوئی پیسے نہ بھیجیں۔",
        "دھوکے والے میسج 7726 (SPAM) پر فارورڈ کریں۔",
        "کینیڈین اینٹی فراڈ سینٹر کو رپورٹ کریں: 1-888-495-8501",
        "اپنے بینک کو اُس نمبر پر کال کریں جو آپ کے کارڈ کی پچھلی طرف لکھا ہے۔",
    ],
    "es": [
        "No toque ningún enlace, no responda y no pague nada.",
        "Reenvíe los mensajes de estafa al 7726 (SPAM).",
        "Repórtelo al Centro Canadiense Antifraude: 1-888-495-8501.",
        "Llame a su banco al número que aparece detrás de su tarjeta.",
    ],
    "ar": [
        "لا تضغط على أي رابط، ولا ترد، ولا تدفع أي مال.",
        "أعد توجيه رسائل الاحتيال إلى 7726 (SPAM).",
        "أبلغ المركز الكندي لمكافحة الاحتيال: 1-888-495-8501",
        "اتصل بالبنك على الرقم المكتوب على ظهر بطاقتك.",
    ],
    "hi": [
        "किसी लिंक पर क्लिक न करें, जवाब न दें और कोई पैसे न भेजें।",
        "धोखे वाले मैसेज 7726 (SPAM) पर फ़ॉरवर्ड करें।",
        "कैनेडियन एंटी-फ्रॉड सेंटर को रिपोर्ट करें: 1-888-495-8501",
        "अपने बैंक को उस नंबर पर कॉल करें जो आपके कार्ड के पीछे लिखा है।",
    ],
    "fr": [
        "Ne cliquez sur aucun lien, ne répondez pas et ne payez rien.",
        "Transférez les textos frauduleux au 7726 (SPAM).",
        "Signalez-le au Centre antifraude du Canada : 1-888-495-8501.",
        "Appelez votre banque au numéro inscrit au dos de votre carte.",
    ],
}

PRIVACY_NOTE = {
    "en": "Your message is checked only on this laptop. It is never sent online.",
    "ur": "آپ کا پیغام صرف اسی لیپ ٹاپ پر چیک ہوتا ہے۔ یہ کبھی انٹرنیٹ پر نہیں بھیجا جاتا۔",
    "es": "Su mensaje se revisa solo en esta computadora. Nunca se envía por internet.",
    "ar": "يتم فحص رسالتك على هذا الجهاز فقط، ولا يتم إرسالها إلى الإنترنت أبداً.",
    "hi": "आपका मैसेज सिर्फ़ इसी लैपटॉप पर चेक होता है। इसे कभी इंटरनेट पर नहीं भेजा जाता।",
    "fr": "Votre message est vérifié uniquement sur cet ordinateur. Il n'est jamais envoyé en ligne.",
}


def _check_all_languages_covered():
    from prompts import LANGUAGES

    for code in LANGUAGES:
        assert code in ACTION_STEPS, f"ACTION_STEPS is missing '{code}'"
        assert code in PRIVACY_NOTE, f"PRIVACY_NOTE is missing '{code}'"
        assert len(ACTION_STEPS[code]) == len(ACTION_STEPS["en"]), f"ACTION_STEPS['{code}'] has the wrong number of steps"


if __name__ == "__main__":
    _check_all_languages_covered()
    print("All languages covered.")
