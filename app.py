import io
import os
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from src.pipeline import normalize_candidates, filter_candidates, make_outreach_drafts
from src.ai_writer import generate_ai_message

load_dotenv()
st.set_page_config(page_title="CreatorReach AI", page_icon="✨", layout="wide")

st.title("✨ CreatorReach AI")
st.caption("Micro-influencer discovery, qualification and outreach workspace")
st.info("This app works with creator data you provide or are authorized to use. It does not scrape Instagram or bypass platform restrictions.")

with st.sidebar:
    st.header("Campaign settings")
    niche = st.text_input("Creator niche", "beauty, skincare, makeup")
    min_followers = st.number_input("Minimum followers", min_value=0, value=5000, step=1000)
    max_followers = st.number_input("Maximum followers", min_value=1, value=100000, step=5000)
    brand = st.text_input("Brand name", "Your Brand")
    product = st.text_input("Product / offer", "Your Product")
    tone = st.selectbox("Message tone", ["Friendly and professional", "Warm and conversational", "Short and direct"])

st.subheader("1. Upload creator candidates")
uploaded = st.file_uploader("Upload CSV", type=["csv"])
if uploaded:
    try:
        raw = pd.read_csv(uploaded)
        st.success(f"Loaded {len(raw)} rows.")
        st.dataframe(raw.head(20), use_container_width=True)
        normalized = normalize_candidates(raw)
        qualified, rejected, review = filter_candidates(
            normalized, [x.strip().lower() for x in niche.split(",") if x.strip()],
            int(min_followers), int(max_followers)
        )
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Candidates", len(normalized))
        c2.metric("Qualified", len(qualified))
        c3.metric("Rejected", len(rejected))
        c4.metric("Needs review", len(review))

        tab1, tab2, tab3 = st.tabs(["Qualified", "Needs review", "Rejected"])
        with tab1:
            st.dataframe(qualified, use_container_width=True)
        with tab2:
            st.dataframe(review, use_container_width=True)
        with tab3:
            st.dataframe(rejected, use_container_width=True)

        st.download_button("Download qualified CSV", qualified.to_csv(index=False).encode("utf-8"), "qualified_influencers.csv", "text/csv")
        st.download_button("Download review CSV", review.to_csv(index=False).encode("utf-8"), "review_influencers.csv", "text/csv")
        st.download_button("Download rejected CSV", rejected.to_csv(index=False).encode("utf-8"), "rejected_influencers.csv", "text/csv")

        st.divider()
        st.subheader("2. Generate outreach drafts")
        use_ai = st.toggle("Use AI copywriting (requires OPENAI_API_KEY)", value=False)
        if st.button("Create personalized drafts", type="primary"):
            drafts = []
            for _, row in qualified.iterrows():
                draft = make_outreach_drafts(row, brand, product, tone)
                if use_ai:
                    draft = generate_ai_message(row.to_dict(), brand, product, tone, draft)
                drafts.append(draft)
            result = qualified.copy()
            if drafts:
                result["email_subject"] = [d["subject"] for d in drafts]
                result["email_message"] = [d["body"] for d in drafts]
                result["outreach_status"] = "Draft - review before sending"
            st.session_state["drafts"] = result
            st.success(f"Created {len(result)} drafts.")

        if "drafts" in st.session_state:
            drafts_df = st.session_state["drafts"]
            st.dataframe(drafts_df[["username", "contact_email", "email_subject", "outreach_status"]], use_container_width=True)
            for _, r in drafts_df.iterrows():
                with st.expander(f"Draft for @{r.get('username', '')}"):
                    st.write("**Subject:**", r.get("email_subject", ""))
                    st.text_area("Message", str(r.get("email_message", "")), height=180, key=f"msg_{r.get('username','')}")
            st.download_button("Download outreach drafts", drafts_df.to_csv(index=False).encode("utf-8"), "outreach_drafts.csv", "text/csv")
    except Exception as exc:
        st.error(f"Could not process CSV: {exc}")
else:
    st.markdown("Upload a CSV with columns such as `username`, `full_name`, `followers`, `category`, `content_themes`, `contact_email`, `profile_url`.")
    demo = pd.DataFrame([
        {"username":"creator_one","full_name":"Creator One","followers":25000,"category":"beauty","content_themes":"skincare routines, makeup reviews","contact_email":"","profile_url":"https://www.instagram.com/creator_one/"},
        {"username":"creator_two","full_name":"Creator Two","followers":18000,"category":"skincare","content_themes":"skin care, beauty tips","contact_email":"hello@example.com","profile_url":"https://www.instagram.com/creator_two/"},
        {"username":"creator_three","full_name":"Creator Three","followers":120000,"category":"fashion","content_themes":"fashion styling","contact_email":"","profile_url":"https://www.instagram.com/creator_three/"}
    ])
    st.caption("Example data (fictional)")
    st.dataframe(demo, use_container_width=True)
    st.download_button("Download sample CSV", demo.to_csv(index=False).encode("utf-8"), "sample_candidates.csv", "text/csv")

st.divider()
st.caption("Privacy-first workflow • No automatic Instagram scraping • No emails sent by this app")
