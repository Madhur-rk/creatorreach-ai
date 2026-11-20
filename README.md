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

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
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
