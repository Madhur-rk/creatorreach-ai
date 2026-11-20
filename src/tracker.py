import sqlite3
from pathlib import Path
import pandas as pd
DB_PATH = Path(__file__).resolve().parents[1] / "creatorreach.db"

def connect():
    conn = sqlite3.connect(DB_PATH); conn.execute("""CREATE TABLE IF NOT EXISTS outreach (
        id INTEGER PRIMARY KEY AUTOINCREMENT, profile_url TEXT UNIQUE, influencer_name TEXT, platform TEXT,
        contact_email TEXT, email_subject TEXT, email_body TEXT, instagram_dm TEXT,
        status TEXT DEFAULT 'Draft', sent_at TEXT, notes TEXT DEFAULT '')"""); conn.commit(); return conn

def upsert_drafts(df):
    conn=connect()
    for _,r in df.iterrows():
        conn.execute("""INSERT INTO outreach(profile_url,influencer_name,platform,contact_email,email_subject,email_body,instagram_dm,status)
        VALUES(?,?,?,?,?,?,?,'Draft') ON CONFLICT(profile_url) DO UPDATE SET influencer_name=excluded.influencer_name,
        platform=excluded.platform,contact_email=excluded.contact_email,email_subject=excluded.email_subject,
        email_body=excluded.email_body,instagram_dm=excluded.instagram_dm""",
        (str(r.get('profile_url','')),str(r.get('full_name') or r.get('username','')),str(r.get('platform','')),
         str(r.get('contact_email','Not Found')),str(r.get('email_subject','')),str(r.get('email_body','')),str(r.get('instagram_dm',''))))
    conn.commit(); conn.close()

def simulate_send(profile_urls):
    conn=connect(); sent=0; skipped=0
    for url in profile_urls:
        row=conn.execute("SELECT contact_email,status FROM outreach WHERE profile_url=?",(url,)).fetchone()
        if not row or not row[0] or row[0]=='Not Found' or '@' not in row[0] or row[1] in ('Simulated Sent','Sent'):
            skipped+=1; continue
        conn.execute("UPDATE outreach SET status='Simulated Sent', sent_at=datetime('now') WHERE profile_url=?",(url,)); sent+=1
    conn.commit(); conn.close(); return sent, skipped

def get_tracker():
    conn=connect(); df=pd.read_sql_query("SELECT * FROM outreach ORDER BY id DESC",conn); conn.close(); return df
