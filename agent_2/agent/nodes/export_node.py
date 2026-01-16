import pandas as pd
import sys
from pathlib import Path
from urllib.parse import quote_plus
import re
import requests
import uuid

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agent.state import AgentState
from config.settings import OUTPUT_CSV


# =====================================================
# HELPERS
# =====================================================

def excel_safe_phone(phone):
    """Make phone Excel-proof"""
    if not phone or str(phone).strip() == "":
        return ""
    phone = str(phone).strip()
    return f'="{phone}"'


def extract_email(html):
    """Extract email from HTML using regex or mailto"""
    if not html:
        return None

    emails = re.findall(
        r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
        html
    )
    if emails:
        return emails[0]

    mailto = re.findall(r"mailto:([^\"'>]+)", html)
    if mailto:
        return mailto[0]

    return None


def fetch_page(url):
    """Simple GET request with safety"""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            return r.text
    except Exception as e:
        print(f"⚠ Failed to fetch {url}: {e}")
    return None


def get_email_for_broker(broker):
    """LEVEL 1 + LEVEL 2 email extraction"""

    listing_html = broker.get("listing_html", "")
    email = extract_email(listing_html)
    if email:
        return email, "listing_page"

    profile_url = broker.get("broker_profile_url", "")
    if profile_url:
        profile_html = fetch_page(profile_url)
        email = extract_email(profile_html)
        if email:
            return email, "broker_profile"

    return None, "none"


# =====================================================
# EXPORT NODE
# =====================================================

def export_brokers_node(state: AgentState) -> AgentState:
    """Export brokers with email enrichment + record_id"""

    print("\n" + "=" * 60)
    print("NODE 2: EXPORT BROKERS TO CSV")
    print("=" * 60)

    brokers = state.get("broker_database", [])

    if not brokers:
        print("⚠ No brokers to export")
        state["current_stage"] = "export_complete"
        return state

    cleaned = []

    for b in brokers:
        broker = b.copy()

        # ----------------- SAFETY: record_id -----------------
        broker.setdefault("record_id", f"broker_{uuid.uuid4().hex}")

        # ----------------- Excel-safe phone -----------------
        broker["phone"] = excel_safe_phone(broker.get("phone"))

        # ----------------- Auto email extraction -----------------
        if not broker.get("email"):
            email, source = get_email_for_broker(broker)
            broker["email"] = email if email else ""
            broker["email_source"] = source
        else:
            broker["email_source"] = "existing"

        # ----------------- LinkedIn search URL -----------------
        name = broker.get("broker_name", "")
        if name and name.lower() != "not available":
            broker["linkedin_search_url"] = (
                f"https://www.linkedin.com/search/results/all/?keywords={quote_plus(name)}"
            )
        else:
            broker["linkedin_search_url"] = ""

        cleaned.append(broker)

    df = pd.DataFrame(cleaned)

    # ----------------- DEDUP (phone is strongest key) -----------------
    if "phone" in df.columns:
        df = df.drop_duplicates(subset=["phone"], keep="first")

    # ----------------- COLUMN ORDER -----------------
    cols = [
        "record_id",
        "broker_name",
        "brokerage_firm",
        "email",
        "email_source",
        "phone",
        "geography",
        "industry_focus",
        "linkedin_search_url",
        "source_listing_url",
        "extraction_timestamp",
    ]

    # keep only existing columns
    cols = [c for c in cols if c in df.columns]
    df = df[cols]

    # ----------------- SAVE CSV -----------------
    df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")

    print(f"\n✓ Exported {len(df)} brokers to: {OUTPUT_CSV}")
    print(f"✓ Valid phones: {(df['phone'] != '').sum() if 'phone' in df else 0}")
    print(f"✓ Valid emails: {(df['email'] != '').sum() if 'email' in df else 0}")

    state["output_path"] = str(OUTPUT_CSV)
    state["current_stage"] = "export_complete"

    return state
