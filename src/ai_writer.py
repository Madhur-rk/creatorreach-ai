<<<<<<< HEAD
import os, json
=======
import os
>>>>>>> origin/main
from openai import OpenAI

def generate_ai_message(creator, brand, product, tone, fallback):
    """Optional AI rewrite. Requires OPENAI_API_KEY and an available model."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return fallback
    client = OpenAI(api_key=api_key)
<<<<<<< HEAD
    safe_creator = {k: creator.get(k) for k in ["full_name", "username", "platform", "category", "content_themes", "recent_content", "profile_url"]}
    prompt = f"""Create a respectful, genuinely personalized first-contact creator collaboration email.
Brand: {brand}
Product/offer: {product}
Tone: {tone}
Verified creator information (use only facts present here): {json.dumps(safe_creator, ensure_ascii=False)}
Rules:
- Email body must be 60-90 words, including greeting and sign-off.
- Instagram DM must be 15-30 words.
- Reference only supplied niche/content information. Do not claim to have watched a recent post unless recent_content explicitly describes one.
- Never invent performance metrics, audience demographics, email addresses, familiarity, promises, or compensation.
- Be natural, specific, concise, and respectful; no pressure.
Return valid JSON with keys subject, body, instagram_dm. Return no markdown.
=======
    prompt = f"""
Write one concise, respectful first-contact influencer collaboration email.
Brand: {brand}
Product: {product}
Tone: {tone}
Creator details: {creator}
Avoid fabricated claims, fake familiarity, pressure, or promises.
Return only JSON with keys subject and body.
>>>>>>> origin/main
"""
    try:
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[{"role":"user","content":prompt}],
<<<<<<< HEAD
            temperature=0.5,
            response_format={"type":"json_object"}
        )
        data = json.loads(response.choices[0].message.content)
        body = str(data.get("body", fallback["body"]))
        dm = str(data.get("instagram_dm", fallback.get("instagram_dm", "")))
        body_words = body.split()
        dm_words = dm.split()
        if len(body_words) > 90: body = " ".join(body_words[:90])
        if len(body.split()) < 60: body = fallback["body"]
        if len(dm_words) > 30: dm = " ".join(dm_words[:30])
        if len(dm.split()) < 15: dm = fallback.get("instagram_dm", "")
        return {"subject": str(data.get("subject", fallback["subject"])), "body": body, "instagram_dm": dm}
=======
            temperature=0.7,
            response_format={"type":"json_object"}
        )
        import json
        data = json.loads(response.choices[0].message.content)
        return {"subject": data.get("subject", fallback["subject"]),
                "body": data.get("body", fallback["body"])}
>>>>>>> origin/main
    except Exception:
        return fallback
