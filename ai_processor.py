"""
ai_processor.py — Groq AI (Llama 3.3 70B) ilə xəbərləri kateqoriyalara ayır
                   və Azerbaycancaya çevir.

API qənaəti strategiyası:
  - Bütün xəbərlər BİR sorğuya yığılır (batch processing)
  - Hər taramada cəmi 1–2 API çağırışı olur
  - Groq pulsuz: gündə 6000 sorğu, dəqiqədə 30 sorğu
"""

import json
import logging
import re
import time
from difflib import SequenceMatcher

from groq import Groq

from config import (
    GROQ_API_KEY,
    GROQ_MODEL_1,
    GROQ_MODEL_3,
    OPENROUTER_API_KEY,
    OPENROUTER_MODEL_2,
    CATEGORIES,
    MIN_IMPORTANCE_SCORE,
    BATCH_SIZE,
    AI_MAX_TOKENS,
    SIMILARITY_THRESHOLD,
    BATCH_DELAY_SECONDS,
)
from usage_memory import update_stats

import requests

logger = logging.getLogger(__name__)

_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None


# ─── Sistem promptu ───────────────────────────────────────────────────────────

_SYSTEM_PROMPT = """Sən texnologiya xəbərlərini Azerbaycancaya çevirən və kateqoriyalara ayıran AI köməkçisisən.

Sənə İngilis dilinde texnologiya xəbərlərinin siyahısı veriləcək.
Hər xəbər üçün aşağıdakıları Azerbaycanca ver:

1. category — aşağıdakılardan birini seç:
   həftənin_hadisəsi  → qlobal miqyasda çox böyük, şok hadisə (hər taramada max 1-2 ədəd)
   süni_intellekt     → AI, ML, LLM, ChatGPT, Gemini, Claude, Copilot, robotlar
   təhlükəsizlik      → kiberhücum, zəiflik, hack, virus, ransomware, CVE, exploit
   məxfilik           → data sızması, izləmə, şifrələmə, VPN, GDPR, surveillance
   avadanlıq          → prosessor, GPU, telefon, laptop, çip, hardware, batareya
   açıq_mənbə         → Linux, open source, GPL, GitHub layihəsi, kernel
   oyun               → video oyun, konsol, Steam, gaming, esports
   azərbaycan_tech    → Azərbaycandakı texnologiya xəbərləri, yerli startaplar, rəqəmsal inkişaflar, Azərbaycanın İKT sahəsindəki yenilikləri, kiber təhlükəsizlik hadisələri
   qeyd_etməyə_dəyər  → texnologiya ilə əlaqəli digər maraqlı xəbərlər

   VACİB: Əgər xəbərdə "İPUCU:" yazısı varsa, category-də HƏMİN dəyəri istifadə et! İpucu həmişə birinci gəlir.

2. title_az — başlığı Azerbaycancaya çevir (tamamilə qısa, 8-10 söz). "Şok sirlər" kimi boş sözlər əlavə etmə!

3. summary_az — BU ÇOX ÖNƏMLİDİR: Başlığı (title_az) eyni ilə təkrarlama! Xəbərin MƏZNUNUNDAN ən dəyərli, fərqli detalları çıxarıb 1-2 cümlə ilə xülasə yaz. Başlığın kopyası OLMASIN.

4. importance — 1-10 əhəmiyyət balı:
   9-10 → Dəhşətli dərəcədə önəmli, "Yusuf İpek" bəhs edəcək qədər kritik texnoloji hadisə
   7-8  → Çox önəmli, ciddi inkişaflar
   5-6  → Adi xəbərlər
   1-4  → Tamamilə lüzumsuz, maraqsız, kiçik detal və ya təkrar xəbərlər. Dəyərsiz xəbərlərə mütləq aşağı bal ver!

CAVAB FORMATİ — yalnız düzgün JSON array, heç bir izah əlavə etmə:
[
  {"index": 0, "category": "...", "title_az": "...", "summary_az": "...", "importance": 7},
  {"index": 1, "category": "...", "title_az": "...", "summary_az": "...", "importance": 5}
]"""


# ─── Batch emal ───────────────────────────────────────────────────────────────

def _build_user_message(articles: list[dict]) -> str:
    lines = ["Aşağıdakı xəbərləri emal et:\n"]
    for i, art in enumerate(articles):
        lines.append(f"[{i}] BAŞLIQ: {art['title']}")
        if art.get("description"):
            lines.append(f"    AÇIQLAMA: {art['description'][:250]}")
        lines.append(f"    MƏNBƏ: {art['source']}")
        if art.get("hint"):
            lines.append(f"    İPUCU: {art['hint']}")
        lines.append("")
    return "\n".join(lines)


def _call_ai(articles: list[dict], model_choice: int = 1) -> list[dict]:
    """Seçilmiş model və ya pilləli fallback ilə xəbərləri emal edir."""
    user_msg = _build_user_message(articles)
    
    # Pilləli ierarxiya: 70B (1) -> Gemma 12B (2) -> 8B (3) -> Mistral 7B (4)
    current_choice = model_choice
    
    # OUTPUT ÜÇÜN MAX_TOKENS ENDİRİLDİ (4096 ÇOX İDİ VƏ 6000 TPM LİMİTİNİ POZURDU)
    MAX_TOK = AI_MAX_TOKENS
    
    if current_choice <= 1:
        try:
            if not _client:
                raise Exception("Groq client mövcud deyil (API key yoxdur)")
            completion = _client.chat.completions.with_raw_response.create(
                model=GROQ_MODEL_1,
                messages=[{"role": "system", "content": _SYSTEM_PROMPT}, {"role": "user", "content": user_msg}],
                temperature=0.2,
                max_tokens=MAX_TOK,
            )
            update_stats("groq_1", completion.headers)
            raw = completion.parse().choices[0].message.content.strip()
            return _extract_json(raw)
        except Exception as e:
            logger.warning("Batch Groq 70B xətası: %s", e)
            current_choice = 2
            
    if current_choice == 2:
        if OPENROUTER_API_KEY:
            try:
                resp = requests.post(
                    url="https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://github.com/XRD-EnDeRmAn/aztech",
                        "X-Title": "AzTech Bot",
                    },
                    json={
                        "model": OPENROUTER_MODEL_2,
                        "messages": [
                            {"role": "system", "content": _SYSTEM_PROMPT},
                            {"role": "user", "content": user_msg},
                        ],
                    },
                    timeout=60,
                )
                if resp.status_code == 200:
                    update_stats("openrouter_2", resp.headers)
                    raw = resp.json()["choices"][0]["message"]["content"].strip()
                    return _extract_json(raw)
                logger.warning("Batch OpenRouter (12B) xətası: %d", resp.status_code)
            except Exception as e:
                logger.warning("Batch OpenRouter (12B) istisna: %s", e)
        current_choice = 3

    if current_choice == 3:
        try:
            if not _client:
                raise Exception("Groq client mövcud deyil")
            completion = _client.chat.completions.with_raw_response.create(
                model=GROQ_MODEL_3,
                messages=[{"role": "system", "content": _SYSTEM_PROMPT}, {"role": "user", "content": user_msg}],
                temperature=0.2,
                max_tokens=MAX_TOK,
            )
            update_stats("groq_3", completion.headers)
            raw = completion.parse().choices[0].message.content.strip()
            return _extract_json(raw)
        except Exception as e:
            logger.warning("Batch Groq 8B xətası: %s", e)
        current_choice = 4

    if current_choice >= 4:
        if OPENROUTER_API_KEY:
            try:
                from config import OPENROUTER_MODEL_4
                resp = requests.post(
                    url="https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://github.com/XRD-EnDeRmAn/aztech",
                        "X-Title": "AzTech Bot",
                    },
                    json={
                        "model": OPENROUTER_MODEL_4,
                        "messages": [
                            {"role": "system", "content": _SYSTEM_PROMPT},
                            {"role": "user", "content": user_msg},
                        ],
                    },
                    timeout=60,
                )
                if resp.status_code == 200:
                    update_stats("openrouter_4", resp.headers)
                    raw = resp.json()["choices"][0]["message"]["content"].strip()
                    return _extract_json(raw)
                logger.error("Batch OpenRouter (Mistral 7B) xətası: %d", resp.status_code)
            except Exception as e:
                logger.error("Batch OpenRouter (Mistral 7B) istisna: %s", e)
                
    logger.error("API Limitlərinin 4-ü də tükəndi!")
    return []

def _extract_json(text: str) -> list[dict]:
    """Mətndən JSON array-i çıxarır."""
    try:
        json_match = re.search(r"\[.*\]", text, re.DOTALL)
        if not json_match:
            return []
        return json.loads(json_match.group())
    except (json.JSONDecodeError, AttributeError):
        return []


# ─── Əsas funksiya ────────────────────────────────────────────────────────────

def process_articles(articles: list[dict], model_choice: int = 1) -> list[dict]:
    """
    Bütün xəbərləri batch ilə AI-a göndər,
    kateqoriyalanmış + Azerbaycanca xəbərlər siyahısı qaytar.
    """
    if not articles:
        return []

    processed: list[dict] = []

    for batch_start in range(0, len(articles), BATCH_SIZE):
        batch = articles[batch_start: batch_start + BATCH_SIZE]
        logger.info(
            "AI batch göndərilir (Seçim: %d): %d xəbər (indeks %d-%d)",
            model_choice, len(batch), batch_start, batch_start + len(batch) - 1,
        )

        ai_results = _call_ai(batch, model_choice)

        for res in ai_results:
            idx = res.get("index", -1)
            if not (0 <= idx < len(batch)):
                continue

            importance = int(res.get("importance", 0))
            if importance < MIN_IMPORTANCE_SCORE:
                continue

            category_key = res.get("category", "qeyd_etməyə_dəyər")
            if category_key not in CATEGORIES:
                category_key = "qeyd_etməyə_dəyər"

            emoji, label = CATEGORIES[category_key]
            original = batch[idx]

            processed.append({
                "title_az":       res.get("title_az", original["title"]),
                "summary_az":     res.get("summary_az", ""),
                "category":       category_key,
                "category_label": label,
                "emoji":          emoji,
                "importance":     importance,
                "link":           original["link"],
                "source":         original["source"],
                "published":      original.get("published"),
            })

        # Batch-lər arası gözlə (TPM limitini qorumaq üçün)
        if batch_start + BATCH_SIZE < len(articles):
            logger.debug("Növbəti batch üçün %d saniyə gözlənilir...", BATCH_DELAY_SECONDS)
            time.sleep(BATCH_DELAY_SECONDS)

    processed.sort(key=lambda x: x["importance"], reverse=True)
    
    # ─── Təkrarların (Duplicatların) Silinməsi (Set tabanlı O(n)) ───
    seen_titles: set[str] = set()
    final_processed = []
    
    for art in processed:
        title_lower = art["title_az"].lower()
        # Set tabanlı tez yoxlama
        if title_lower in seen_titles:
            continue
        
        # Mürəkkəb yoxlama (similarity)
        is_dup = False
        for seen_title in seen_titles:
            similarity = SequenceMatcher(None, title_lower, seen_title).ratio()
            if similarity > SIMILARITY_THRESHOLD:
                is_dup = True
                break
        
        if not is_dup:
            seen_titles.add(title_lower)
            final_processed.append(art)

    logger.info(
        "AI emalı tamamlandı: %d orijinal xəbər filtrdən keçdi (Ümumi: %d)",
        len(final_processed), len(articles),
    )
    return final_processed


def group_by_category(articles: list[dict]) -> dict[str, list[dict]]:
    """Xəbərləri kateqoriya açarına görə qruplaşdır (sabit sıra ilə)."""
    grouped: dict[str, list[dict]] = {key: [] for key in CATEGORIES}
    for art in articles:
        key = art["category"]
        grouped.setdefault(key, []).append(art)
    return grouped
