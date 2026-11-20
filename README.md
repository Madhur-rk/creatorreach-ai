<<<<<<< HEAD
# CreatorReach – Micro-Influencer Outreach Tool

CreatorReach is a Streamlit project for collecting creator details, checking whether they fit a campaign, preparing outreach messages and keeping a record of follow-ups.

## What it can do

- Search YouTube channels with the YouTube Data API.
- Upload creator details from a CSV file.
- Clean up column names and remove duplicate profile links.
- Filter creators by topic, follower count and (when available) engagement rate.
- Put records with missing information into a review list.
- Prepare an email and an Instagram DM draft for each qualified creator.
- Save draft and simulated-send status in a local SQLite database.
- Export the lists and outreach log as CSV files.

## Run it on Windows

Open PowerShell in this folder and run:
=======
# CreatorReach AI — Automated Micro-Influencer Outreach

A Streamlit workspace for importing creator candidates, qualifying them by niche and follower range, and drafting personalized outreach messages.

## Features
- CSV upload and normalization
- Duplicate and username validation
- Configurable niche and follower filters
- Qualified / review / rejected lists
- Template-based personalized outreach
- Optional AI rewriting through the OpenAI API
- CSV downloads for results and drafts
- No automated Instagram scraping and no automatic email sending

## Run locally (Windows PowerShell)
>>>>>>> origin/main

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
<<<<<<< HEAD
streamlit run app.py
```

Then open `http://localhost:8501` in your browser.

## YouTube API key

YouTube search needs a YouTube Data API v3 key. Create a key in Google Cloud Console and enable the YouTube Data API v3 for the project. For local use, put the key in a `.env` file:

```text
YOUTUBE_API_KEY=your_key_here
```

Do not upload `.env` or share your key publicly. If the app is deployed on Streamlit Community Cloud, add the key in the app's Secrets settings instead.

The OpenAI rewrite option is optional. It needs an `OPENAI_API_KEY`. The normal message templates work without it.

## CSV columns

The app can use these columns:

`username`, `full_name`, `platform`, `followers`, `engagement_rate`, `category`, `content_themes`, `contact_email`, `profile_url`, `website`, `source`, `recent_content`, `geography`.

Some common alternatives are also accepted, such as `name`, `email`, `niche`, `subscribers`, `url` and `engagement`.

Keep the source and profile link for each record so the details can be checked later.

## A few things to know

- The sample CSV contains made-up example records. It is only there to show the expected format.
- YouTube search finds YouTube channels; it does not find Instagram accounts. Subscriber counts should not be treated as Instagram follower counts.
- The app only picks up an email if it is written in the public YouTube channel description. Many channels will not have one.
- Engagement rate and audience demographics are not guessed. If a value is missing, check the creator manually or leave it unavailable.
- The app does not send real emails. The send option only changes the status in the local tracker.
- Instagram messages have to be sent manually.
- YouTube API results and quota depend on the API and the search term. A search may return fewer than 50 useful channels.

## Files

- `app.py` – Streamlit interface
- `src/discovery.py` – YouTube channel search
- `src/pipeline.py` – data cleanup, filtering and message templates
- `src/ai_writer.py` – optional OpenAI message rewrite
- `src/tracker.py` – SQLite outreach log
- `data/sample_candidates.csv` – example CSV with fictional records

## Before submitting

Use real records collected from sources that allow this use, check the details, and keep the source links. Do not present the sample rows as real creators. Test the app locally and take screenshots of the working version. Keep API keys and private contact details out of the repository.
=======
Copy-Item .env.example .env
# Edit .env and add OPENAI_API_KEY if you want AI rewriting
streamlit run app.py
```

The app opens at http://localhost:8501.

## Input CSV columns
Required: `username`, `followers`

Recommended: `full_name`, `category`, `content_themes`, `contact_email`, `profile_url`, `source`.

A sample CSV can be downloaded from the app.

## Deploy on Streamlit Community Cloud
1. Push this folder to a GitHub repository.
2. Sign in to Streamlit Community Cloud and create an app from that repository.
3. Select `app.py` as the entry point.
4. Add `OPENAI_API_KEY` and `OPENAI_MODEL` in the app's Secrets settings if using AI.
5. Deploy. The hosted URL will be provided by Streamlit.

## GitHub
Suggested repository name: `creatorreach-ai-micro-influencer-outreach`.

```bash
git init
git add .
git commit -m "Initial CreatorReach AI app"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/creatorreach-ai-micro-influencer-outreach.git
git push -u origin main
```

## Important
- Candidate data must be collected lawfully and in line with Instagram's terms and applicable privacy laws.
- This app does not discover Instagram accounts automatically.
- Verify all creator details and review every message before contacting anyone.
- Never commit API keys, passwords, or private creator data to GitHub.
>>>>>>> origin/main
