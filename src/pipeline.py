import re
import pandas as pd

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
