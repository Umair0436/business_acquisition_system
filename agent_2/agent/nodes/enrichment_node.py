from urllib.parse import quote
import sys
from pathlib import Path
import re
import requests

# Fix imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agent.state import AgentState
from config.settings import LINKEDIN_SEARCH_TEMPLATE


# ---------------- EMAIL EXTRACTOR ----------------
def extract_email(html):
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


def enrich_brokers_node(state: AgentState) -> AgentState:
    """
    NODE 4:
    - Email enrichment (LEVEL 1)
    - Geography mapping
    - Industry focus mapping
    - LinkedIn search URL
    """

    print("\n" + "="*60)
    print("NODE 4: BROKER ENRICHMENT")
    print("="*60)

    brokers = state.get("broker_database", [])
    enriched_count = 0

    for broker in brokers:

        # ---------------- EMAIL (LEVEL 1) ----------------
        if not broker.get("email"):
            listing_html = broker.get("listing_html", "")
            email = extract_email(listing_html)
            if email:
                broker["email"] = email
                broker["email_source"] = "listing_page"

        # ---------------- GEOGRAPHY ----------------
        if not broker.get("geography"):
            broker["geography"] = (
                broker.get("listing_location")
                or broker.get("location")
                or ""
            )

        # ---------------- INDUSTRY FOCUS ----------------
        if not broker.get("industry_focus"):
            broker["industry_focus"] = (
                broker.get("listing_industry")
                or broker.get("industry")
                or ""
            )

        # ---------------- LINKEDIN URL ----------------
        name = broker.get("broker_name", "")
        firm = broker.get("brokerage_firm", "")

        if name:
            linkedin_url = LINKEDIN_SEARCH_TEMPLATE.format(
                name=quote(name),
                firm=quote(firm) if firm else ""
            )
            broker["linkedin_search_url"] = linkedin_url

        enriched_count += 1

    state["broker_database"] = brokers
    state["current_stage"] = "enrichment_complete"

    print(f"✓ Enriched {enriched_count} brokers")
    print(f"✓ Emails found: {sum(1 for b in brokers if b.get('email'))}")
    print(f"✓ Geography filled: {sum(1 for b in brokers if b.get('geography'))}")
    print(f"✓ Industry filled: {sum(1 for b in brokers if b.get('industry_focus'))}")

    return state
