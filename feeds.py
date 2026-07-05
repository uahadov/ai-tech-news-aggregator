"""
feeds.py — Etibarlı xəbər mənbələri (RSS URL-ləri)

Kateqoriyalar:
  - təhlükəsizlik: Kiber təhlükəsizlik xəbərləri
  - süni_intellekt: AI, ML xəbərləri
  - avadanlıq: Hardware xəbərləri
  - açıq_mənbə: Open source xəbərləri
  - oyun: Gaming xəbərləri
  - məxfilik: Privacy xəbərləri
  - azərbaycan_tech: Azərbaycan texnologiya xəbərləri
  - None: Ümumi texnologiya xəbərləri
"""

RSS_FEEDS = [
    # ── Azərbaycan Texnologiya Xəbərləri ──────────────────────────────────────
    {
        "url": "https://techxeber.az/rss.xml",
        "name": "Tech Xəbər (AZ)",
        "hint": "azərbaycan_tech",
    },
    {
        "url": "https://technote.az/rss.xml",
        "name": "Technote.az",
        "hint": "azərbaycan_tech",
    },

    # ── Azərbaycan Təhlükəsizlik Xəbərləri ────────────────────────────────────
    {
        "url": "https://cert.gov.az/en/rss",
        "name": "Azerbaijan CERT",
        "hint": "təhlükəsizlik",
    },

    # ── Qlobal Təhlükəsizlik ──────────────────────────────────────────────────
    {
        "url": "https://www.bleepingcomputer.com/feed/",
        "name": "BleepingComputer",
        "hint": "təhlükəsizlik",
    },
    {
        "url": "https://krebsonsecurity.com/feed/",
        "name": "Krebs on Security",
        "hint": "təhlükəsizlik",
    },
    {
        "url": "https://feeds.feedburner.com/TheHackersNews",
        "name": "The Hacker News",
        "hint": "təhlükəsizlik",
    },
    {
        "url": "https://www.darkreading.com/rss.xml",
        "name": "Dark Reading",
        "hint": "təhlükəsizlik",
    },
    {
        "url": "https://www.securityweek.com/feed",
        "name": "SecurityWeek",
        "hint": "təhlükəsizlik",
    },
    {
        "url": "https://securityaffairs.com/feed",
        "name": "SecurityAffairs",
        "hint": "təhlükəsizlik",
    },
    {
        "url": "https://www.schneier.com/feed/atom/",
        "name": "Schneier on Security",
        "hint": "təhlükəsizlik",
    },

    # ── Məxfilik (Privacy) ────────────────────────────────────────────────────
    {
        "url": "https://pogowasright.org/feed/",
        "name": "Privacy News (POGO)",
        "hint": "məxfilik",
    },
    {
        "url": "https://www.eff.org/rss/updates.xml",
        "name": "EFF Updates",
        "hint": "məxfilik",
    },
    {
        "url": "https://datamatters.sidley.com/feed",
        "name": "Sidley Data Privacy",
        "hint": "məxfilik",
    },

    # ── Süni İntellekt & Ümumi Tech ──────────────────────────────────────────
    {
        "url": "https://feeds.arstechnica.com/arstechnica/index",
        "name": "Ars Technica",
        "hint": None,
    },
    {
        "url": "https://www.theverge.com/rss/index.xml",
        "name": "The Verge",
        "hint": None,
    },
    {
        "url": "https://www.wired.com/feed/rss",
        "name": "Wired",
        "hint": None,
    },
    {
        "url": "https://techcrunch.com/feed/",
        "name": "TechCrunch",
        "hint": None,
    },
    {
        "url": "https://www.technologyreview.com/feed/",
        "name": "MIT Technology Review",
        "hint": "süni_intellekt",
    },
    {
        "url": "https://venturebeat.com/feed/",
        "name": "VentureBeat",
        "hint": "süni_intellekt",
    },
    {
        "url": "https://www.artificialintelligence-news.com/feed/",
        "name": "AI News",
        "hint": "süni_intellekt",
    },

    # ── Avadanlıq ──────────────────────────────────────────────────────────────
    {
        "url": "https://www.tomshardware.com/feeds/all",
        "name": "Tom's Hardware",
        "hint": "avadanlıq",
    },
    {
        "url": "https://www.engadget.com/rss.xml",
        "name": "Engadget",
        "hint": None,
    },

    # ── Açıq Mənbə & Linux ────────────────────────────────────────────────────
    {
        "url": "https://www.phoronix.com/rss.php",
        "name": "Phoronix",
        "hint": "açıq_mənbə",
    },
    {
        "url": "https://lwn.net/headlines/rss",
        "name": "LWN.net",
        "hint": "açıq_mənbə",
    },
    {
        "url": "https://itsfoss.com/feed/",
        "name": "It's FOSS",
        "hint": "açıq_mənbə",
    },

    # ── Oyun ───────────────────────────────────────────────────────────────────
    {
        "url": "https://www.pcgamer.com/rss/",
        "name": "PC Gamer",
        "hint": "oyun",
    },
    {
        "url": "https://www.gamespot.com/feeds/mashup/",
        "name": "GameSpot",
        "hint": "oyun",
    },
    {
        "url": "https://feeds.feedburner.com/ign/games-all",
        "name": "IGN Games",
        "hint": "oyun",
    },
    {
        "url": "https://www.vg247.com/feed",
        "name": "VG247",
        "hint": "oyun",
    },
    {
        "url": "https://www.polygon.com/rss/index.xml",
        "name": "Polygon",
        "hint": "oyun",
    },
    {
        "url": "https://www.rockpapershotgun.com/feed",
        "name": "Rock Paper Shotgun",
        "hint": "oyun",
    },
    {
        "url": "https://www.digitaltrends.com/gaming/feed/",
        "name": "Digital Trends Gaming",
        "hint": "oyun",
    },

    # ── Apple & Mobil ──────────────────────────────────────────────────────────
    {
        "url": "https://9to5mac.com/feed/",
        "name": "9to5Mac",
        "hint": "avadanlıq",
    },
    {
        "url": "https://9to5google.com/feed/",
        "name": "9to5Google",
        "hint": "avadanlıq",
    },

]
