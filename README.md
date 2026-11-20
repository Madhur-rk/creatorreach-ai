# CreatorReach AI — Automated Micro-Influencer Outreach System

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
Every discovered creator is evaluated against four automated rules and assigned a `PASS` or `FAIL` status with an explicit `Filter Reason`:
1. **Follower Range:** `5,000 <= followers <= 100,000`
2. **Engagement Rate:** `>= 2.0%` average across recent videos
3. **Channel Activity:** `>= 10` published videos
4. **Niche Relevance & Brand Safety:** Keyword relevance score `>= 0.25` and zero brand-safety exclusion hits

Shortlisted creators are further classified into **Tier 1 (High Priority Fit)**, **Tier 2 (Strong Fit)**, or **Tier 3 (Standard Fit)**.

### 4. AI Model, Prompt & Personalization Logic (`src/personalization.py`, `src/prompts.py`)
* Uses `gemini-2.5-flash` with `response_mime_type="application/json"` to guarantee structured output.
* Injects each creator's name, niche, follower count, engagement rate, content themes, and **up to 3 recent video titles** into the prompt so every message is genuinely unique.
* Enforces strict word-count validation with an automatic retry loop:
  * **Email Pitch:** `60–90 words`
  * **Instagram DM:** `15–30 words`

### 5. Sending Mechanism (`src/sender.py`, `src/storage.py`)
* Selects only shortlisted creators with a valid contact email (`!= "Not Found"`).
* Checks `data/outreach.db` (SQLite) before sending to strictly prevent duplicate outreach across runs.
* Defaults to **Dry-Run Simulation Mode** (`SIMULATED_SENT`) for safe testing; pass `--send-live` with Gmail App Password credentials in `.env` for live SMTP delivery.
* **Instagram DM Compliance:** Rather than violating Meta/Instagram Terms of Service with unauthorized bots, the pipeline exports a ready-to-use `outputs/instagram_dm_queue.csv` with each creator's IG profile URL and copy-paste DM.

---

## Project Structure

```text
creatorreach-ai/
├── main.py                  # End-to-end CLI pipeline entrypoint
├── requirements.txt         # Python dependencies
├── .env.example             # API key & brand configuration template
├── .gitignore               # Excludes .env, caches, and local DB
├── README.md                # Project documentation
├── src/
│   ├── config.py            # Niche presets & filtering thresholds
│   ├── models.py            # Dataclass schemas
│   ├── discovery.py         # Stage 1: YouTube Data API v3 discovery
│   ├── enrichment.py        # Stage 2: Public email, links, and themes
│   ├── filtering.py         # Stage 3: PASS/FAIL classification & tiers
│   ├── prompts.py           # Structured JSON LLM prompts
│   ├── personalization.py   # Stage 4: Gemini outreach generation
│   ├── sender.py            # Stage 5: Gmail SMTP & dry-run dispatch
│   └── storage.py           # SQLite deduplication & CSV exports
├── tests/
│   └── test_pipeline.py     # Offline unit tests
└── outputs/                 # Generated CSV deliverables
```

---

## Setup & Usage Instructions

### 1. Clone & Install Dependencies
```bash
git clone [https://github.com/Madhur-rk/creatorreach-ai.git](https://github.com/Madhur-rk/creatorreach-ai.git)
cd creatorreach-ai
python -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment Variables
```bash
cp .env.example .env
```
Open `.env` and add:
* `YOUTUBE_API_KEY` — Free from [Google Cloud Console](https://console.cloud.google.com/) (enable **YouTube Data API v3**)
* `GEMINI_API_KEY` — Free from [Google AI Studio](https://aistudio.google.com/app/apikey)
* *(Optional)* `SMTP_USERNAME` & `SMTP_PASSWORD` (Gmail App Password) if running `--send-live`

### 3. Run the Pipeline
```bash
# Default safe run (Technology niche, 60 creators, dry-run email simulation)
python main.py --niche "Technology" --target-count 60

# Other built-in niches: "Fitness", "Fashion & Beauty", "Fintech"
python main.py --niche "Fashion & Beauty" --target-count 60

# Live email sending via Gmail SMTP (only after reviewing outputs!)
python main.py --niche "Technology" --target-count 60 --send-live
```

### 4. Run Automated Unit Tests
```bash
python -m unittest discover -s tests -v
```

---

## Generated Output Files

After running `python main.py`, the following deliverables are created in `outputs/`:
1. `outputs/influencers_dataset.csv` — All 50+ discovered influencers with metrics, enrichment fields, `Status` (`PASS`/`FAIL`), and `Filter Reason`.
2. `outputs/personalized_messages.csv` — Shortlisted creators with AI-generated Email Subject, Email Pitch (60–90 words), Instagram DM (15–30 words), and Collaboration Angle.
3. `outputs/outreach_tracker.csv` — Complete outreach log with delivery status, timestamp, and deduplication tracking.
4. `outputs/instagram_dm_queue.csv` — Compliant manual sending queue for Instagram DMs.

---

## Limitations & Scalability Notes
* **Email Availability:** Only creators who publicly list an email in their YouTube channel description can be contacted automatically; YouTube's CAPTCHA-gated email button is intentionally not bypassed.
* **Audience Demographics:** Exact age/gender breakdowns are private to channel owners via YouTube Analytics API and are transparently marked unavailable.
* **Scaling to 500+ Influencers:** The modular architecture supports scaling by rotating search queries, batching `channels.list` calls (50 IDs/request), adding async concurrency (`asyncio`/`httpx`), and swapping SQLite for PostgreSQL.
