# 🤖 AzTech — Süni İntellekt Dəstəkli Texnologiya Xəbər və Məzmun Botu

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python" alt="Python Version" />
  <img src="https://img.shields.io/badge/Telegram-Bot%20API-2CA5E0?style=for-the-badge&logo=telegram" alt="Telegram API" />
  <img src="https://img.shields.io/badge/AI-Groq%20%7C%20Llama%203.3%2070B-orange?style=for-the-badge" alt="AI Provider" />
  <img src="https://img.shields.io/badge/Deployment-Render%20%7C%20GitHub%20Actions-brightgreen?style=for-the-badge" alt="Deployment" />
  <img src="https://img.shields.io/badge/Dil-Az%C9%99rbaycan-red?style=for-the-badge" alt="Dil" />
</p>

---

## 📌 Bu Proqram Nədir və Nə İşə Yarayır?

**AzTech** — dünyanın və Azərbaycanın ən etibarlı 28+ texnologiya mənbəsini (kiber təhlükəsizlik, süni intellekt, proqramlaşdırma, qadcetlər, açıq mənbə və s.) 7/24 izləyən, vacib xəbərləri Süni İntellektlə seçib **təmiz Azərbaycan dilində** Telegram kanalınıza və ya şəxsi çatınıza çatdıran ağıllı köməkçidir.

Bu sadəcə xəbər paylaşan bot deyil; eyni zamanda **texnologiya bloggerləri, media kanalları və kontent yaradıcıları üçün şəxsi AI asistandır**. Bot vasitəsilə bircə əmrlə istənilən xəbərdən saniyələr içində **YouTube/TikTok video ssenarisi**, **Instagram postu**, **dərin texniki analiz** çıxara və ya xəbərlə bağlı botun özünə sual verə bilərsiniz.

---

## ✨ Əsas İmkanları

* **🌐 28+ Yerli və Qlobal Mənbə:** CERT.gov.az, Technote.az, TechXəbər, BleepingComputer, Krebs on Security, The Hacker News, Dark Reading, TechCrunch, Verge və daha onlarla etibarlı RSS axını.
* **🧠 Qabaqcıl AI Filtrləməsi:** Xəbərlər dərhal Llama 3.3 70B (Groq) tərəfindən oxunur, 1-10 bal arası əhəmiyyəti qiymətləndirilir və lazımsız "klikbeyt" məlumatlar kənara atılır.
* **🇦🇿 Təmiz Azərbaycan Dili:** Qəlib tərcümələrdən və yad qrammatikadan uzaq, səlis və anlaşıqlı ana dili təminatı.
* **🎬 Kontent İstehsalı (YouTube / Reels / TikTok):** Bəyəndiyiniz xəbərin ID-sini göndərməklə birbaşa video ssenarisi (`/script 1 60`) və ya qısa sosial media postu (`/short 1`) hazırlamaq imkanı.
* **💬 Xəbərə Dair Sual-Cavab (`/ask`):** Məqalədə aydın olmayan məqamı bota soruşun, bot orijinal mətni araşdırıb cavablasın.
* **🗳 İcma Səsverməsi:** Hər xəbərin altında 👍 / 👎 düymələri ilə oxucuların maraq dairəsini ölçmək və ən populyar xəbərləri görmək.
* **📰 Həftəlik Bülleten:** Hər həftənin sonunda həftənin ən önəmli hadisələrini cəmləyən xüsusi icmal bülleteni (`/bulent`).
* **🔄 Kəsintisiz Ehtiyat Modellər:** Groq limiti bitərsə, avtomatik OpenRouter və digər ehtiyat modellərə (Gemma 12B, Llama 8B, Mistral) keçid edir.
* **☁️ 0 Xərclə İşləmə:** Həm Render.com (Webhook), həm şəxsi kompüter/VPS, həm də heç bir server olmadan **tamamilə pulsuz GitHub Actions** üzərində işləyə bilir.

---

## 🕹 Telegram Bot Əmrləri

Botu işə saldıqdan sonra çatda aşağıdakı əmrlərdən istifadə edə bilərsiniz:

| Əmr | Təyinatı | Nümunə |
| :--- | :--- | :--- |
| `/tarama` | Yeni xəbərləri dərhal yoxlayır və kanala göndərir (Llama 70B ilə) | `/tarama` |
| `/tarama2` | Alternativ model (Gemma 12B) ilə tarama edir | `/tarama2` |
| `/script <id> [saniyə]` | Xəbərdən vaxt kodlu YouTube / TikTok ssenarisi yazır | `/script 3 60` |
| `/short <id>` | Instagram / Telegram üçün cəlbedici qısa post hazırlayır | `/short 2` |
| `/deep <id>` | Xəbərin arxa planını və texniki detallarını dərin izah edir | `/deep 5` |
| `/ask <id> <sual>` | Xəbər barədə xüsusi sualınızı cavablandırır | `/ask 1 Bu problem kimlərə təsir edir?` |
| `/bulent` | Həftənin ən mühüm texnoloji hadisələrinin bülletenini göndərir | `/bulent` |
| `/stats` | Botun iş vaxtı, cəmi xəbərlər və ən çox səs toplayan TOP xəbərlər | `/stats` |
| `/limit` | Süni İntellekt modellərinin qalan sorğu və token limitlərini göstərir | `/limit` |
| `/help` | Əmrlər siyahısını göstərir | `/help` |

---

## 🚀 Quraşdırma və İlk İşə Salma

### 1. Tələblər
* Python 3.10 və ya daha yeni versiya
* Telegram Hesabı (Bot yaratmaq üçün)
* Pulsuz [Groq Cloud](https://console.groq.com) hesabı (API açarı üçün)

---

### 2. Layihəni Klonlayın və Asılılıqları Quraşdırın

```bash
# Repozitoriyanı yükləyin
git clone https://github.com/uahadov/aztech.git
cd aztech

# Virtual mühit yaradın və aktivləşdirin
python -m venv venv

# Windows üçün:
venv\Scripts\activate
# Linux/macOS üçün:
source venv/bin/activate

# Paketləri quraşdırın
pip install -r requirements.txt
```

---

### 3. Tənzimləmələri Edun (`.env`)

Layihədəki `.env.example` faylının nüsxəsini çıxarıb `.env` adlandırın:

```bash
cp .env.example .env
```

`.env` faylını açıb lazımi məlumatları qeyd edin:

```env
# 1. Telegram məlumatları (@BotFather-dan əldə edin)
TELEGRAM_BOT_TOKEN=123456789:ABCdefGhIJKlmNoPQRstuvWXyz
TELEGRAM_CHAT_ID=-1001234567890   # Kanalınızın və ya şəxsi çatınızın ID-si

# 2. Pulsuz Groq API Açarı (https://console.groq.com ünvanından alın)
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxx

# 3. Könüllü Ehtiyat AI Açarı (OpenRouter)
OPENROUTER_API_KEY=

# 4. Tarama Tənzimləmələri
SCAN_INTERVAL_HOURS=6      # Neçə saatdan bir avtomatik tarasın
MIN_IMPORTANCE_SCORE=6     # 1-10 arası min əhəmiyyət dərəcəsi (6 və yuxarı seçilir)
MAX_ARTICLES_PER_RUN=40    # Hər taramada maksimum baxılacaq xəbər sayı
```

> 💡 **Köməkçi İpucu:** Şəxsi Telegram Chat ID-nizi asanlıqla öyrənmək üçün bota `/start` yazdıqdan sonra bu skripti işə sala bilərsiniz:
> ```bash
> python get_chat_id.py
> ```

---

### 4. Bağlantını Yoxlayın

Hər şeyin düzgün quraşdırıldığından əmin olmaq üçün konfiqurasiya yoxlayıcısını işə salın:

```bash
python main.py --check
```
*(Bütün bəndlər `✅` olaraq göstərilməli və Telegram/Groq ilə əlaqə təsdiqlənməlidir).*

---

### 5. Botu İşə Salın

İstəyinizə uyğun olaraq 3 rejimdə işə sala bilərsiniz:

#### A Rejimi: Yalnız bir dəfə sınaq üçün tarama
```bash
python main.py --test
```

#### B Rejimi: Şəxsi kompüterdə/VPS-də daimi rejim
```bash
python main.py
```
*(Dərhal ilk taramanı aparır və təyin etdiyiniz saat intervalı ilə arxa planda işləməyə davam edir).*

#### C Rejimi: Webhook / Render.com rejimi
```bash
python web.py
```
*(Flask serverini işə salır və Telegram-dan gələn interaktiv əmrləri dərhal cavablayır).*

---

## 🌐 Server Olmadan Tamamilə Pulsuz İşlətmək

Əgər şəxsi serveriniz və ya daimi açıq kompüteriniz yoxdursa, layihəyə daxil edilmiş **GitHub Actions** vasitəsilə botu heç bir qəpik xərcləmədən işlədə bilərsiniz:

1. Reponuzu GitHub-a yükləyin.
2. Repo daxilində **Settings** ➡️ **Secrets and variables** ➡️ **Actions** bölməsinə keçin.
3. Aşağıdakı gizli açarları əlavə edin:
   * `TELEGRAM_BOT_TOKEN`
   * `TELEGRAM_CHAT_ID`
   * `GROQ_API_KEY`
4. Bot hər 6 saatdan bir `.github/workflows/bot.yml` vasitəsilə avtomatik işə düşəcək və yeni xəbərləri kanalınıza yönləndirəcək!

---

## 📁 Layihənin Fayl Strukturu

```text
├── .github/workflows/
│   └── bot.yml                 # Pulsuz GitHub Actions avtomatlaşdırması
├── ai_content_generator.py     # Ssenari (/script), post (/short) və analiz generatoru
├── ai_processor.py             # Xəbərlərin qiymətləndirilməsi və dublikat filtri
├── bulletin.py                 # Həftəlik bülleten modulu
├── config.py                   # Bütün tənzimləmələr və kateqoriya tərifləri
├── feeds.py                    # 28+ etibarlı RSS mənbə siyahısı
├── get_chat_id.py              # Telegram Chat ID öyrənmək üçün köməkçi skript
├── main.py                     # Əsas giriş nöqtəsi və konsol interfeysi
├── news_memory.py              # Xəbər ID-ləri və keş yaddaşı
├── requirements.txt            # Lazımi Python kitabxanaları
├── rss_reader.py               # RSS axınlarını oxuyan və təmizləyən modul
├── scheduler.py                # Avtomatik vaxt cədvəli
├── telegram_bot.py             # Telegram mesajlaşma və bildiriş nüvəsi
├── usage_memory.py             # API limit və token statistikası
├── votes.py                    # Oxucu səsvermə sistemi (👍/👎)
├── web.py                      # Render.com və Flask Webhook serveri
└── .env.example                # Nümunə mühit dəyişənləri
```

---

## 📄 Lisenziya və Dəstək

Bu layihə açıq mənbəlidir. Hər hansı təklif, sual və ya xəta bildirişi üçün [Issues](https://github.com/uahadov/aztech/issues) bölməsindən müraciət edə və ya Pull Request göndərə bilərsiniz.
