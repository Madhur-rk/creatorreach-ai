import os
from openai import OpenAI

def generate_ai_message(creator, brand, product, tone, fallback):
    """Optional AI rewrite. Requires OPENAI_API_KEY and an available model."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return fallback
    client = OpenAI(api_key=api_key)
    prompt = f"""
Write one concise, respectful first-contact influencer collaboration email.
Brand: {brand}
Product: {product}
Tone: {tone}
Creator details: {creator}
Avoid fabricated claims, fake familiarity, pressure, or promises.
Return only JSON with keys subject and body.
"""
    try:
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[{"role":"user","content":prompt}],
            temperature=0.7,
            response_format={"type":"json_object"}
        )
        import json
        data = json.loads(response.choices[0].message.content)
        return {"subject": data.get("subject", fallback["subject"]),
                "body": data.get("body", fallback["body"])}
    except Exception:
        return fallback
