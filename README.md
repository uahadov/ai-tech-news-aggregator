# 🤖 AzTech — AI-Powered Tech News & Content Creation Bot

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python" alt="Python Version" />
  <img src="https://img.shields.io/badge/Telegram-Bot%20API-2CA5E0?style=for-the-badge&logo=telegram" alt="Telegram API" />
  <img src="https://img.shields.io/badge/AI-Groq%20%7C%20Llama%203.3%2070B-orange?style=for-the-badge" alt="AI Provider" />
  <img src="https://img.shields.io/badge/Deployment-Render%20%7C%20GitHub%20Actions-brightgreen?style=for-the-badge" alt="Deployment" />
  <img src="https://img.shields.io/badge/License-MIT-purple?style=for-the-badge" alt="License" />
</p>

---

## 📌 What is AzTech?

**AzTech** is an automated 24/7 Telegram bot that monitors **28+ top global and local tech & cybersecurity news outlets**. Powered by high-speed Large Language Models (Groq's **Llama 3.3 70B** with fallbacks to **Gemma** and **Mistral**), AzTech evaluates, filters out clickbait, removes duplicates, and delivers clean, high-value tech news summaries directly to your Telegram channel or chat.

More than just a news feeder, AzTech serves as an **AI content copilot for tech creators, journalists, and media channels**. With a single command, you can turn any breaking news item into a **timed video script for YouTube/TikTok/Reels**, a **concise social media post**, an **in-depth technical breakdown**, or ask questions about the article directly to the bot.

---

## ✨ Key Features

* **🌐 28+ Verified Feeds:** Tracks major security and tech sources including *CERT.gov.az, Technote.az, TechXəbər, BleepingComputer, Krebs on Security, The Hacker News, Dark Reading, TechCrunch, The Verge*, and more.
* **🧠 Smart AI Filtering & Scoring:** Rates every incoming article on an importance scale (1–10). Low-relevance items and clickbait are discarded automatically.
* **🇦🇿 Native Language Output:** Summaries and scripts are produced in clean, natural Azerbaijani with accurate technical terminology.
* **🎬 Instant Content Creation:**
  * **Video Scripts (`/script <id> [seconds]`):** Generates full spoken scripts with visual scene cues and pacing suitable for YouTube or TikTok.
  * **Shorts & Posts (`/short <id>`):** Creates punchy, emoji-spaced posts ready for Instagram, X (Twitter), or Telegram.
  * **Deep Analysis (`/deep <id>`):** Explains root causes, architectural impact, and future implications of complex tech events.
* **💬 Interactive Q&A (`/ask <id> <question>`):** Asks the AI questions about a specific article; the bot scrapes the full source article and answers accurately.
* **🗳 Community Feedback:** Includes inline 👍 and 👎 buttons on every broadcasted news post, tracking community sentiment and top-ranked stories (`/stats`).
* **📰 Weekly Digest (`/bulent`):** Automatically compiles a curated weekly technology recap.
* **🔄 Seamless Multi-Model Fallback:** If Groq limits are reached, the bot automatically fails over to OpenRouter (Gemma 12B, Llama 8B, Mistral 7B) without downtime.
* **☁️ 100% Free Hosting Options:** Can run continuously on a VPS, as a webhook on Render.com, or **completely serverless and free via GitHub Actions**.

---

## 🕹 Telegram Bot Commands

| Command | Description | Example |
| :--- | :--- | :--- |
| `/tarama` | Scan for latest news immediately using **Llama 3.3 70B** | `/tarama` |
| `/tarama2` | Scan using secondary model (**Gemma 3 12B**) | `/tarama2` |
| `/script <id> [sec]` | Generate a YouTube/TikTok video script with timestamps | `/script 3 60` |
| `/short <id>` | Generate a short, formatted social media post | `/short 2` |
| `/deep <id>` | Generate an in-depth technical analysis of the article | `/deep 5` |
| `/ask <id> <query>` | Ask any question regarding the article | `/ask 1 Who is affected by this vulnerability?` |
| `/bulent` | Generate the weekly tech digest | `/bulent` |
| `/stats` | View uptime, memory size, and community vote rankings | `/stats` |
| `/limit` | Check live remaining API rate limits and token quotas | `/limit` |
| `/help` | Display the command list | `/help` |

---

## 🚀 Quickstart Guide

### 1. Prerequisites
* **Python 3.10+**
* A **Telegram Bot Token** (get one from [@BotFather](https://t.me/BotFather))
* Your **Telegram Chat ID** (where news will be delivered)
* A free **Groq API Key** (from [console.groq.com](https://console.groq.com))

---

### 2. Clone & Setup Environment

```bash
# Clone the repository
git clone https://github.com/uahadov/aztech.git
cd aztech

# Create and activate a virtual environment
python -m venv venv

# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

### 3. Configure Environment Variables (`.env`)

Copy the template file to create your `.env` configuration:

```bash
cp .env.example .env
```

Open `.env` and fill in your values:

```env
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=123456789:ABCdefGhIJKlmNoPQRstuvWXyz
TELEGRAM_CHAT_ID=-1001234567890   # Channel ID or your personal chat ID

# Groq AI Key (Free at https://console.groq.com)
GROQ_API_KEY=gsk_your_groq_api_key_here

# Optional: OpenRouter fallback key (https://openrouter.ai)
OPENROUTER_API_KEY=

# Scanner Settings
SCAN_INTERVAL_HOURS=6      # Interval between automatic scans (hours)
MIN_IMPORTANCE_SCORE=6     # Minimum AI score (1-10) required to publish
MAX_ARTICLES_PER_RUN=40    # Maximum articles evaluated per cycle
```

> 💡 **Tip:** Need to find your Chat ID? Send `/start` to your bot, then run:
> ```bash
> python get_chat_id.py
> ```

---

### 4. Verify Configuration

Run the built-in diagnostic test to verify API keys and network connectivity:

```bash
python main.py --check
```

*(You should see green checkmarks `✅` confirming connections to both Telegram and Groq).*

---

### 5. Running the Bot

You can run AzTech in one of three ways:

#### Option A: One-Off Test Run
Runs a single scan, posts qualifying news, and exits:
```bash
python main.py --test
```

#### Option B: Continuous Local / VPS Scheduler
Runs an initial scan immediately, then stays alive to scan periodically:
```bash
python main.py
```

#### Option C: Webhook Server (Render.com / Production)
Runs the Flask HTTP server to handle real-time Telegram button clicks and commands:
```bash
python web.py
```

---

## ⚡ Zero-Cost Serverless Setup (GitHub Actions)

If you don't want to run a 24/7 server, you can run AzTech **completely free** using GitHub Actions:

1. Push this repository to your GitHub account.
2. Go to your repo **Settings** ➡️ **Secrets and variables** ➡️ **Actions**.
3. Add the following repository secrets:
   * `TELEGRAM_BOT_TOKEN`
   * `TELEGRAM_CHAT_ID`
   * `GROQ_API_KEY`
4. The workflow in `.github/workflows/bot.yml` will automatically run every 6 hours via Cron, check feeds, update `seen_news.json`, and send updates directly to your Telegram.

---

## 📁 Repository Structure

```text
├── .github/workflows/
│   └── bot.yml                 # Automated 6-hour cron workflow via GitHub Actions
├── ai_content_generator.py     # Scriptwriting, short posts, and deep analysis logic
├── ai_processor.py             # Deduplication, relevance scoring, and translation
├── bulletin.py                 # Weekly digest compiler
├── config.py                   # Central settings, model fallbacks, and categories
├── feeds.py                    # List of 28+ curated RSS feed endpoints
├── get_chat_id.py              # Utility to retrieve Telegram Chat IDs
├── main.py                     # CLI entry point, scheduler, and self-test suite
├── news_memory.py              # In-memory mapping of articles to sequential IDs
├── requirements.txt            # Python dependencies
├── rss_reader.py               # Feed parsing and text sanitization
├── scheduler.py                # Periodic task runner (APScheduler)
├── telegram_bot.py             # Telegram messaging layer and button handlers
├── usage_memory.py             # Live API token and rate limit trackers
├── votes.py                    # Interactive thumbs up / thumbs down tally
├── web.py                      # Flask webhook server for interactive commands
└── .env.example                # Sample environment configuration file
```

---

## 🤝 Contributing & License

Contributions, bug reports, and suggestions are welcome! Feel free to open an issue or submit a pull request.

This project is licensed under the [MIT License](LICENSE).
