"""AI saralash. Claude API ishlamasa yoki kalit bo'lmasa — oddiy kalit so'z qoidalari.
AI faqat tavsiya beradi, yakuniy qarorni operator qabul qiladi."""
import json
import logging
import re
from dataclasses import dataclass

import httpx

from .. import config

log = logging.getLogger("smartsos.ai")

TRIAGE_PROMPT = (
    "Sen favqulodda chaqiruvlarni saralash yordamchisisan. "
    "Xizmatlar: 101 - favqulodda vaziyat (yong'in), 102 - ichki ishlar, "
    "103 - tez yordam, 104 - gaz xizmati. "
    'Faqat JSON qaytar, boshqa matn yozma: '
    '{"services":"103,101","severity":"HIGH|MEDIUM|LOW","summary":"qisqa o\'zbekcha xulosa"}'
)


@dataclass
class Result:
    services: str
    severity: str
    summary: str
    ai: bool


def _ask(system: str, user: str, max_tokens: int) -> str:
    """Claude API ga so'rov yuboradi, javob matnini qaytaradi."""
    resp = httpx.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": config.ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": config.ANTHROPIC_MODEL,
            "max_tokens": max_tokens,
            "system": system,
            "messages": [{"role": "user", "content": user}],
        },
        timeout=15.0,
    )
    resp.raise_for_status()
    return resp.json()["content"][0]["text"]


def triage(text: str) -> Result:
    """Matnni tahlil qiladi. Har qanday xatoda qoidalarga qaytadi."""
    if not config.ANTHROPIC_API_KEY:
        return rules(text)
    try:
        raw = re.sub(r"```(?:json)?", "", _ask(TRIAGE_PROMPT, text, 300)).strip()
        data = json.loads(raw)
        services = str(data.get("services", ""))
        severity = str(data.get("severity", "")).upper()
        if not re.fullmatch(r"10[1-4](,10[1-4])*", services) or severity not in ("HIGH", "MEDIUM", "LOW"):
            return rules(text)
        return Result(services, severity, str(data.get("summary", "")), True)
    except Exception as e:  # noqa: BLE001
        log.warning("Claude API ishlamadi, qoidalarga o'tildi: %s", e)
        return rules(text)


def chat_reply(specialty: str, text: str) -> str:
    """Mutaxassis chati uchun AI javobi (tashxis va dori dozasi aytilmaydi)."""
    fallback = "AI hozir mavjud emas. Jiddiy holatda darhol 103 ga qo'ng'iroq qiling."
    if not config.ANTHROPIC_API_KEY:
        return fallback
    system = (
        f'Sen "{specialty}" yo\'nalishidagi AI yordamchisan (haqiqiy shifokor emassan). '
        "Tashxis qo'yma va dori dozasini aytma. Umumiy maslahat ber. "
        "Jiddiy belgilar bo'lsa 103 ga qo'ng'iroq qilishni ayt. Qisqa, o'zbekcha javob yoz."
    )
    try:
        return _ask(system, text, 400)
    except Exception as e:  # noqa: BLE001
        log.warning("Chat AI xatosi: %s", e)
        return fallback


def _has(t: str, *words: str) -> bool:
    return any(w in t for w in words)


def rules(raw: str) -> Result:
    """Zaxira usul: kalit so'zlar bo'yicha (o'zbek va rus)."""
    t = re.sub(r"[’‘ʻʼ`]", "'", (raw or "").lower())
    s: list[str] = []
    if _has(t, "nafas", "hush", "yurak", "qon", "og'ri", "tug'ish", "zaharlan", "jarohat",
            "bemor", "дыш", "сердц", "кровь", "скорая"):
        s.append("103")
    if _has(t, "yong'in", "tutun", "olov", "portlash", "suv bosdi", "пожар", "огонь"):
        s.append("101")
    if _has(t, "o'g'ri", "talon", "hujum", "qurol", "urishyapti", "avariya", "вор", "грабеж"):
        s.append("102")
    if _has(t, "gaz", "hidi", "газ"):
        s.append("104")
    if not s:
        s.append("103")

    severity = "LOW"
    if _has(t, "og'ri", "jarohat", "avariya", "hujum", "gaz", "hidi"):
        severity = "MEDIUM"
    if _has(t, "hushidan", "nafas ol", "qon ket", "yong'in", "portlash", "qurol", "yurak",
            "tug'ish", "не дышит"):
        severity = "HIGH"
    return Result(",".join(s), severity,
                  "Oddiy qoidalar (AI ulanmagan). Yakuniy qarorni operator qabul qiladi.", False)
