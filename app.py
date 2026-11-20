<<<<<<< HEAD
import os, io
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from src.pipeline import normalize_candidates, filter_candidates, make_outreach_drafts
from src.ai_writer import generate_ai_message
from src.discovery import discover_youtube
from src.tracker import upsert_drafts, simulate_send, get_tracker

load_dotenv()
st.set_page_config(page_title="CreatorReach", page_icon="📣", layout="wide")
st.title("CreatorReach")
st.caption("A small tool for finding creators and managing collaboration outreach.")
st.info("Use creator information from public or approved sources. This app does not scrape Instagram or send Instagram DMs. Missing information is left blank or marked as unavailable.")

with st.sidebar:
    st.header("Campaign details")
    niche = st.text_input("Niche / discovery keyword", "fitness")
    min_followers = st.number_input("Minimum followers", min_value=0, value=5000, step=1000)
    max_followers = st.number_input("Maximum followers", min_value=1, value=100000, step=5000)
    min_engagement = st.number_input("Minimum engagement rate (%) — 0 disables", min_value=0.0, max_value=100.0, value=0.0, step=0.5)
    brand = st.text_input("Brand name", "Your Brand")
    product = st.text_input("Product / offer", "Your Product")
    tone = st.selectbox("Message tone", ["Friendly and professional", "Warm and conversational", "Short and direct"])
    use_ai = st.toggle("Use OpenAI enhancement", value=False, help="Requires OPENAI_API_KEY in environment or Streamlit Secrets.")

if "candidates" not in st.session_state: st.session_state.candidates = pd.DataFrame()
if "qualified" not in st.session_state: st.session_state.qualified = pd.DataFrame()
if "drafts" not in st.session_state: st.session_state.drafts = pd.DataFrame()

tabs = st.tabs(["Find creators", "Filter list", "Messages", "Outreach log", "About this project"])
with tabs[0]:
    st.subheader("Find creators or upload a CSV")
    left,right=st.columns(2)
    with left:
        st.markdown("**Official YouTube discovery**")
        st.caption("Uses YouTube Data API v3. API key is required; the API returns public channel metrics and descriptions. Public email is extracted only if explicitly listed in the description.")
        try:
            secret_youtube_key = st.secrets.get("YOUTUBE_API_KEY", "")
        except Exception:
            secret_youtube_key = ""
        yt_key = st.text_input("YouTube API key", value=os.getenv("YOUTUBE_API_KEY", secret_youtube_key), type="password")
        target = st.number_input("Maximum channels to fetch", min_value=1, max_value=50, value=50)
        if st.button("Discover YouTube channels", type="primary"):
            try:
                with st.spinner("Querying YouTube Data API..."):
                    discovered=discover_youtube(niche,yt_key,int(target))
                st.session_state.candidates=normalize_candidates(discovered)
                st.success(f"Retrieved {len(discovered)} public channels. Some fields may be unavailable or hidden by the source.")
            except Exception as e: st.error(f"Discovery failed: {e}")
    with right:
        st.markdown("**Import candidate CSV**")
        up=st.file_uploader("CSV from approved sources / manual research",type=["csv"],key="candidate_upload")
        if up is not None:
            try:
                imported=normalize_candidates(pd.read_csv(up))
                st.session_state.candidates=imported
                st.success(f"Imported {len(imported)} unique creator records.")
            except Exception as e: st.error(f"Could not read CSV: {e}")
    if not st.session_state.candidates.empty:
        st.metric("Unique candidate records",len(st.session_state.candidates))
        st.dataframe(st.session_state.candidates, use_container_width=True, hide_index=True)
        st.download_button("Download normalized dataset",st.session_state.candidates.to_csv(index=False).encode(),"influencer_dataset.csv","text/csv")
    else:
        st.warning("No candidate records loaded yet. Use official YouTube discovery with an API key or import a CSV. The included sample is explicitly fictional and must not be submitted as real influencer data.")

with tabs[1]:
    st.subheader("Filter the creator list")
    if st.session_state.candidates.empty: st.info("Load records in Discovery & Data first.")
    else:
        qualified,rejected,review=filter_candidates(st.session_state.candidates,[x.strip() for x in niche.split(",") if x.strip()],int(min_followers),int(max_followers),float(min_engagement))
        st.session_state.qualified=qualified
        a,b,c=st.columns(3); a.metric("Qualified",len(qualified)); b.metric("Rejected",len(rejected)); c.metric("Needs review",len(review))
        q1,q2,q3=st.tabs(["Qualified","Needs review","Rejected"])
        with q1: st.dataframe(qualified,use_container_width=True,hide_index=True)
        with q2: st.dataframe(review,use_container_width=True,hide_index=True)
        with q3: st.dataframe(rejected,use_container_width=True,hide_index=True)
        for label,frame in [("qualified",qualified),("needs_review",review),("rejected",rejected)]:
            st.download_button(f"Download {label}",frame.to_csv(index=False).encode(),f"{label}.csv","text/csv",key=f"dl_{label}")

with tabs[2]:
    st.subheader("Prepare collaboration messages")
    if st.session_state.qualified.empty: st.info("No qualified records yet. Load and qualify candidates first.")
    else:
        if st.button("Generate messages for qualified creators",type="primary"):
            output=[]
            for _,r in st.session_state.qualified.iterrows():
                draft=make_outreach_drafts(r,brand,product,tone)
                if use_ai:
                    ai=generate_ai_message(r.to_dict(),brand,product,tone,{"subject":draft["subject"],"body":draft["email_body"]})
                    draft["subject"]=ai.get("subject",draft["subject"]); draft["email_body"]=ai.get("body",draft["email_body"]); draft["instagram_dm"]=ai.get("instagram_dm",draft["instagram_dm"])
                output.append({**r.to_dict(),"email_subject":draft["subject"],"email_body":draft["email_body"],"instagram_dm":draft["instagram_dm"],"email_word_count":len(draft["email_body"].split()),"dm_word_count":len(draft["instagram_dm"].split()),"outreach_status":"Draft"})
            st.session_state.drafts=pd.DataFrame(output)
            if not st.session_state.drafts.empty: upsert_drafts(st.session_state.drafts)
            st.success(f"Generated and saved {len(output)} personalized draft records.")
        if not st.session_state.drafts.empty:
            st.dataframe(st.session_state.drafts[["full_name","platform","contact_email","email_word_count","dm_word_count","outreach_status"]],use_container_width=True,hide_index=True)
            for i,r in st.session_state.drafts.iterrows():
                with st.expander(f"{r.get('full_name') or r.get('username')} — {r.get('platform')}"):
                    st.caption(f"Email: {r.get('email_word_count')} words | DM: {r.get('dm_word_count')} words")
                    st.text_input("Subject",str(r.get("email_subject","")),key=f"sub_{i}")
                    st.text_area("Email pitch",str(r.get("email_body","")),height=190,key=f"email_{i}")
                    st.text_area("Instagram DM (manual only)",str(r.get("instagram_dm","")),height=90,key=f"dm_{i}")
            st.download_button("Download personalized messages",st.session_state.drafts.to_csv(index=False).encode(),"personalized_outreach.csv","text/csv")

with tabs[3]:
    st.subheader("Outreach log")
    st.warning("Simulation only: no email or Instagram message is actually sent. Instagram DMs must be sent manually unless an approved official API workflow is available.")
    tracker=get_tracker()
    if not tracker.empty:
        st.dataframe(tracker,use_container_width=True,hide_index=True)
        eligible=tracker[(tracker.contact_email.notna())&(tracker.contact_email!="Not Found")&(tracker.contact_email.str.contains("@",na=False))&(tracker.status=="Draft")]
        st.write(f"Eligible for simulated email sending: **{len(eligible)}**")
        selected=st.multiselect("Choose records to mark as simulated sent",eligible.profile_url.tolist(),format_func=lambda x: next((n for n,u in zip(eligible.influencer_name,eligible.profile_url) if u==x),x))
        if st.button("Simulate sending selected emails"):
            sent,skipped=simulate_send(selected); st.success(f"Marked {sent} as Simulated Sent. Skipped {skipped} (missing email, duplicate, or not found).")
            st.rerun()
        st.download_button("Export outreach tracker",tracker.to_csv(index=False).encode(),"outreach_tracker.csv","text/csv")
    else: st.info("Generate outreach messages to create tracker entries.")

with tabs[4]:
    st.subheader("How the project works")
    st.markdown("""
**Workflow:** discovery/import → normalization/deduplication → filtering → message generation → review → simulated sending → SQLite tracker.

- **Discovery:** official YouTube Data API v3 channel search (requires your API key); or import data collected from approved public directories / authorized sources.
- **Enrichment:** channel/profile URL, public subscriber count, channel description/content context, and public email only when explicitly present. Missing email/engagement metrics are not guessed.
- **Filtering:** niche keyword, follower range, optional engagement threshold; records with missing evidence go to Needs review.
- **AI:** optional OpenAI rewrite; deterministic fallback available. Review all messages before contact.
- **Sending:** simulated email status only; no outbound email is sent. Instagram DM workflow is manual.
- **Storage:** SQLite database in the project directory; export CSV for submission.
- **Limitations:** YouTube API quota and hidden subscriber counts; API discovery is not Instagram discovery; audience demographics and engagement rate may not be publicly available.

See README for setup, configuration and submission checklist.
""")

st.divider(); st.caption("CreatorReach • Student project prototype")
=======
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
>>>>>>> origin/main
