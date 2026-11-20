# Automated Micro-Influencer Outreach System

An end-to-end, modular Python pipeline that discovers real micro-influencers (5,000–100,000 followers), enriches their public profiles, filters and classifies them by niche and engagement criteria, generates personalized email pitches and Instagram DMs using an LLM, and dispatches outreach with SQLite duplicate prevention and tracking.

---

## Workflow Architecture

```text
YouTube Data API v3 (Discovery: 50+ Real Creators)
        │
        ▼
Profile Enrichment (Public Email, IG/TikTok/Website, Content Themes)
        │
        ▼
Filtering & Classification (Followers, Engagement Rate, Activity, Niche Fit -> PASS / FAIL)
        │
        ▼
AI Personalization (Gemini API -> 60-90w Email Pitch + 15-30w Instagram DM)
        │
        ▼
Sending Layer (Gmail SMTP / Safe Dry-Run + SQLite Deduplication + Manual IG DM Queue)
        │
        ▼
Structured CSV Deliverables (Dataset, Messages, Outreach Tracker)
```

---

## Technology Stack & APIs Used

| Component | Technology / API | Purpose |
| :--- | :--- | :--- |
| Core Language | Python 3.10+ | Modular pipeline, CLI, data processing |
| Discovery & Metrics | **YouTube Data API v3** | Real channel discovery, subscriber counts, and recent video engagement stats |
| AI Personalization | **Google Gemini API (`google-genai`)** | Dynamic JSON generation of tailored email pitches and Instagram DMs |
| Data Processing | Python `dataclasses` & Pandas | Structured schemas and clean CSV deliverable exports |
| Deduplication & Logging | SQLite (`sqlite3`) | Persistent outreach history to prevent duplicate emails |
| Email Delivery | Python `smtplib` (Gmail SMTP) | Live email delivery or safe dry-run simulation |
| Resilience | `tenacity` | Exponential backoff retry logic for API calls |

---

## Methodology

### 1. Data Sources & Discovery (`src/discovery.py`)
* Queries the official **YouTube Data API v3** across multiple niche-specific search terms (`Technology`, `Fitness`, `Fashion & Beauty`, `Fintech`).
* Collects **60+ unique candidate channels** per test run (exceeding the 50-influencer requirement).
* Pulls channel metadata (`channels.list`) and each creator's 5 most recent uploads (`playlistItems.list` + `videos.list`) to compute a real, verifiable **Engagement Rate**:

$$\text{Engagement Rate} = \frac{\text{Likes} + \text{Comments}}{\text{Views}} \times 100$$

### 2. Profile Enrichment (`src/enrichment.py`)
* Extracts publicly listed business contact emails from channel descriptions using regex filtering. **If no email is listed, the field is explicitly marked `"Not Found"`—no emails are ever guessed or fabricated.**
* Extracts linked Instagram URLs, TikTok URLs, personal websites, channel country (`audience_geography`), and derives `content_themes` from descriptions and recent video titles.
* Audience age and gender are explicitly labeled `"Not Available (Requires Creator Analytics)"` since third-party APIs do not expose private YouTube Studio demographics.

### 3. Filtering & Classification (`src/filtering.py`)
Every discovered creator is evaluated against four automated rules and assigned a `PASS` or `FAIL
