import re
import pandas as pd

<<<<<<< HEAD
BASE_COLUMNS = ["username", "full_name", "platform", "followers", "engagement_rate", "category", "content_themes", "contact_email", "profile_url", "website", "source", "recent_content", "geography"]

def normalize_candidates(df: pd.DataFrame) -> pd.DataFrame:
    data = df.copy()
    aliases = {"name":"full_name", "creator_name":"full_name", "subscribers":"followers", "email":"contact_email", "niche":"category", "url":"profile_url", "platform_name":"platform", "engagement":"engagement_rate"}
    data.columns = [aliases.get(str(c).strip().lower(), str(c).strip().lower()) for c in data.columns]
    for col in BASE_COLUMNS:
        if col not in data.columns:
            data[col] = ""
    data["username"] = data["username"].fillna("").astype(str).str.strip().str.replace("@", "", regex=False)
    data["full_name"] = data["full_name"].fillna("").astype(str).str.strip()
    data["platform"] = data["platform"].replace("", "Instagram").fillna("Instagram").astype(str)
    data["followers"] = pd.to_numeric(data["followers"], errors="coerce")
    data["engagement_rate"] = pd.to_numeric(data["engagement_rate"].astype(str).str.replace("%", "", regex=False), errors="coerce")
    for col in ["category", "content_themes", "contact_email", "profile_url", "source", "recent_content", "website", "geography"]:
        data[col] = data[col].fillna("").astype(str).str.strip()
    data["contact_email"] = data["contact_email"].replace("", "Not Found")
    data["email_valid"] = data["contact_email"].apply(lambda x: bool(re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", x)) if x != "Not Found" else False)
    data["username_valid"] = data.apply(lambda r: bool(r["profile_url"]) or bool(re.fullmatch(r"[A-Za-z0-9._-]{1,100}", r["username"])), axis=1)
    data["profile_url"] = data.apply(lambda r: r["profile_url"] or (f"https://www.instagram.com/{r['username']}/" if r["username"] and r["platform"].lower()=="instagram" else (f"https://www.youtube.com/channel/{r['username']}" if r["username"] and r["platform"].lower()=="youtube" else "")), axis=1)
    dedupe_key = data["profile_url"].where(data["profile_url"].ne(""), data["platform"].str.lower()+":"+data["username"].str.lower())
    data = data.loc[~dedupe_key.duplicated()].reset_index(drop=True)
    return data

def filter_candidates(df, niches, min_followers=5000, max_followers=100000, min_engagement=0):
    qualified, rejected, review = [], [], []
    keywords = [n.strip().lower() for n in niches if n.strip()]
    for _, row in df.iterrows():
        reasons, unknown = [], []
        if not row.get("username_valid", False): reasons.append("Missing or invalid profile identifier")
        followers = row["followers"]
        if pd.isna(followers): unknown.append("Follower count unavailable")
        elif not min_followers <= followers <= max_followers: reasons.append("Follower count outside target range")
        haystack = f"{row['category']} {row['content_themes']} {row['recent_content']}".lower()
        if keywords and not any(k in haystack for k in keywords): unknown.append("Niche relevance not confirmed")
        er = row.get("engagement_rate")
        if min_engagement > 0 and pd.isna(er): unknown.append("Engagement rate unavailable")
        elif min_engagement > 0 and er < min_engagement: reasons.append("Engagement rate below minimum")
        item = row.to_dict()
        if reasons:
            item["filter_reason"] = "; ".join(reasons); rejected.append(item)
        elif unknown:
            item["filter_reason"] = "; ".join(unknown); review.append(item)
        else:
            item["filter_reason"] = "Passed configured filters"; qualified.append(item)
    return tuple(pd.DataFrame(x) for x in (qualified, rejected, review))

def make_outreach_drafts(row, brand, product, tone):
    name = str(row.get("full_name") or row.get("username") or "there").strip()
    niche = str(row.get("category") or "your niche").strip()
    themes = str(row.get("content_themes") or row.get("recent_content") or "your creator content").strip()
    themes = themes[:180]
    opening = f"I found your {niche} work, especially the content around {themes}." if themes else f"I found your work in {niche} and wanted to reach out."
    subject = f"Creator collaboration idea | {brand}"
    body = (f"Hi {name},\n\n{opening} The way you make this topic useful for your audience caught our attention. "
            f"I'm reaching out from {brand} because we are exploring a creator collaboration featuring {product}. "
            f"We think a thoughtful demonstration or honest review could introduce the product to people already interested in {niche}. "
            f"If this sounds relevant, would you be open to sharing your media kit, rates, and preferred collaboration format? "
            f"There is no obligation, and we would be happy to share more campaign details first.\n\nBest,\n{brand}")
    dm = f"Hi {name}! Loved your {niche} content on {themes[:55]}. Would you be open to exploring a {brand} collaboration?"
    # Keep assignment word ranges without inventing creator-specific claims.
    words = body.replace("\n", " ").split()
    if len(words) > 90:
        body = " ".join(words[:90])
    elif len(words) < 60:
        body = body.replace("Thanks for your time", "We would be glad to answer questions and share the proposed brief. Thanks for your time")
    dm_words = dm.split()
    if len(dm_words) > 30: dm = " ".join(dm_words[:30])
    return {"subject": subject, "email_body": body, "instagram_dm": dm, "email_word_count": len(body.split()), "dm_word_count": len(dm.split())}
=======
REQUIRED = ["username", "followers"]

def normalize_candidates(df: pd.DataFrame) -> pd.DataFrame:
    data = df.copy()
    for col in ["username", "full_name", "followers", "category", "content_themes", "contact_email", "profile_url", "source"]:
        if col not in data.columns:
            data[col] = ""
    data["username"] = data["username"].fillna("").astype(str).str.strip().str.replace("@", "", regex=False)
    data["followers"] = pd.to_numeric(data["followers"], errors="coerce")
    data["category"] = data["category"].fillna("").astype(str).str.lower().str.strip()
    data["content_themes"] = data["content_themes"].fillna("").astype(str).str.lower()
    data["contact_email"] = data["contact_email"].fillna("").astype(str).str.strip()
    data["profile_url"] = data.apply(
        lambda r: r["profile_url"] if str(r["profile_url"]).strip() else
        (f"https://www.instagram.com/{r['username']}/" if r["username"] else ""), axis=1
    )
    data["username_valid"] = data["username"].apply(lambda x: bool(re.fullmatch(r"[A-Za-z0-9._]{1,30}", x)))
    data = data.drop_duplicates(subset=["username"], keep="first")
    return data.reset_index(drop=True)

def filter_candidates(df, niches, min_followers=5000, max_followers=100000):
    qualified, rejected, review = [], [], []
    keywords = [n.strip().lower() for n in niches if n.strip()]
    for _, row in df.iterrows():
        reasons = []
        if not row["username_valid"]:
            reasons.append("Invalid or missing Instagram username")
        followers = row["followers"]
        if pd.isna(followers) or not min_followers <= followers <= max_followers:
            reasons.append("Follower count outside target range or missing")
        if reasons:
            item = row.copy()
            item["filter_reason"] = "; ".join(reasons)
            rejected.append(item)
            continue
        haystack = f"{row['category']} {row['content_themes']}".lower()
        if not any(k in haystack for k in keywords):
            item = row.copy()
            item["filter_reason"] = "Niche relevance not confirmed"
            review.append(item)
            continue
        item = row.copy()
        item["filter_reason"] = "Missing contact email" if not row["contact_email"] else ""
        qualified.append(item)
    cols = list(df.columns) + (["filter_reason"] if "filter_reason" not in df.columns else [])
    return (pd.DataFrame(qualified, columns=cols),
            pd.DataFrame(rejected, columns=cols),
            pd.DataFrame(review, columns=cols))

def make_outreach_drafts(row, brand, product, tone):
    name = str(row.get("full_name", "")).strip() or str(row.get("username", "")).strip() or "there"
    themes = str(row.get("content_themes", "")).strip()
    personal = f"I came across your content about {themes} and liked the focus of your work." if themes else "I came across your creator profile and wanted to reach out."
    subject = f"Potential creator collaboration with {brand}"
    if tone == "Short and direct":
        body = f"""Hi {name},\n\n{personal}\n\nI'm reaching out from {brand} to explore a possible collaboration featuring {product}. If you're open to it, could you share your rates or media kit?\n\nBest,\n{brand}"""
    elif tone == "Warm and conversational":
        body = f"""Hi {name},\n\nHope you're doing well! {personal}\n\nWe're {brand}, and we'd love to explore whether a collaboration around {product} could be a good fit for your audience. If you're interested, please share your media kit or collaboration details.\n\nThanks for your time,\n{brand}"""
    else:
        body = f"""Hi {name},\n\n{personal}\n\nI'm contacting you on behalf of {brand}. We are exploring creator partnerships and would be interested in discussing a potential collaboration featuring {product}. If this is relevant to you, please share your media kit and current collaboration rates.\n\nBest regards,\n{brand}"""
    return {"subject": subject, "body": body}
>>>>>>> origin/main
