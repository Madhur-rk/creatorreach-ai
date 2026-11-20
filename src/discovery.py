import os, re, requests
import pandas as pd

YOUTUBE_SEARCH = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_CHANNELS = "https://www.googleapis.com/youtube/v3/channels"

def discover_youtube(query: str, api_key: str, max_results: int = 50):
    """Discover public YouTube channels through the official YouTube Data API v3."""
    if not api_key:
        raise ValueError("Add a YouTube Data API key in Streamlit Secrets or YOUTUBE_API_KEY environment variable.")
    found, page_token = [], None
    while len(found) < max_results:
        params = {"part":"snippet", "q":query, "type":"channel", "maxResults":min(50, max_results-len(found)), "key":api_key}
        if page_token: params["pageToken"] = page_token
        resp = requests.get(YOUTUBE_SEARCH, params=params, timeout=25); resp.raise_for_status()
        payload = resp.json()
        ids = [x["id"]["channelId"] for x in payload.get("items", []) if x.get("id", {}).get("channelId")]
        if ids:
            detail = requests.get(YOUTUBE_CHANNELS, params={"part":"snippet,statistics,brandingSettings", "id":",".join(ids), "key":api_key}, timeout=25)
            detail.raise_for_status()
            for ch in detail.json().get("items", []):
                sn, st, branding = ch.get("snippet", {}), ch.get("statistics", {}), ch.get("brandingSettings", {}).get("channel", {})
                cid = ch.get("id", "")
                desc = sn.get("description", "")
                emails = re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", desc)
                found.append({"username":cid, "full_name":sn.get("title", ""), "platform":"YouTube", "followers":int(st.get("subscriberCount", 0)) if st.get("hiddenSubscriberCount") is False else None,
                    "engagement_rate":"", "category":query, "content_themes":desc[:500], "contact_email":emails[0] if emails else "Not Found",
                    "profile_url":f"https://www.youtube.com/channel/{cid}", "website":"", "source":"YouTube Data API v3", "recent_content":"Channel description: "+desc[:250], "geography":sn.get("country", "")})
        page_token = payload.get("nextPageToken")
        if not page_token or not ids: break
    return pd.DataFrame(found[:max_results])
