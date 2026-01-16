import sys
import re
from pathlib import Path
from datetime import datetime
from agent.state import AgentState, BrokerRecord

# Path fix
agent2_root = Path(__file__).resolve().parent.parent.parent
if str(agent2_root) not in sys.path:
    sys.path.insert(0, str(agent2_root))

from utils.scraper import BrokerScraper, random_delay


def deep_extraction_node(state: AgentState) -> AgentState:
    """Extract broker data (FINAL FIXED VERSION)"""

    print("\n" + "=" * 60)
    print("🤖 NODE 2: DEEP EXTRACTION & VALIDATION")
    print("=" * 60)

    listings = state.get("listings_to_process", [])
    if not listings:
        print("⚠ No listings found.")
        state["broker_database"] = []
        return state

    scraper = BrokerScraper()
    extracted = []
    processed = 0

    for idx, listing in enumerate(listings, 1):
        listing_url = listing.get("Listing URL", "")
        if not listing_url:
            continue

        print(f"\n[{idx}/{len(listings)}] Processing: {listing_url[:80]}...")

        try:
            # ---------------- BASE RECORD ----------------
            broker_record: BrokerRecord = {
                "broker_name": listing.get("Broker or Seller Contact") or "Not Available",
                "brokerage_firm": "Independent",
                "email": None,
                "phone": None,
                "industry_focus": listing.get("Industry") or "General",
                "geography": listing.get("Location") or "Not Specified",
                "linkedin_search_url": None,
                "source_listing_url": listing_url,
                "extraction_timestamp": datetime.now().isoformat()
            }

            # ---------------- DEEP EXTRACTION ----------------
            try:
                broker_data = scraper.extract_broker_data(listing_url)

                # ---- Broker Name (CRITICAL FIX)
                scraped_name = (
                    broker_data.get("broker_name")
                    or broker_data.get("contact_name")
                    or broker_data.get("agent_name")
                )

                if scraped_name and scraped_name.lower() not in [
                    "contact broker", "view profile", "seller"
                ]:
                    broker_record["broker_name"] = scraped_name.strip()
                    print(f"  ✓ Broker Name: {broker_record['broker_name']}")

                # ---- Brokerage Firm
                firm = (
                    broker_data.get("firm")
                    or broker_data.get("brokerage_firm")
                    or broker_data.get("company")
                )

                if firm:
                    broker_record["brokerage_firm"] = firm.strip()
                    print(f"  ✓ Firm: {broker_record['brokerage_firm']}")

                # ---- Email (IMPROVED LOGIC)
                email = (
                    broker_data.get("email")
                    or broker_data.get("mailto_email")
                    or broker_data.get("decoded_email")
                )

                if email and "@" in email:
                    broker_record["email"] = email.lower()
                    print(f"  ✓ Email: {email}")

                # ---- Phone (ALREADY CORRECT – kept safe)
                raw_phone = broker_data.get("phone")
                if raw_phone:
                    digits = re.sub(r"\D", "", str(raw_phone))
                    if len(digits) >= 10:
                        clean_phone = f"+1-{digits[-10:-7]}-{digits[-7:-4]}-{digits[-4:]}"
                        broker_record["phone"] = clean_phone
                        print(f"  ✓ Phone Saved: {clean_phone}")

                # ---- Geography enrichment
                broker_record["geography"] = (
                    broker_data.get("location")
                    or broker_record["geography"]
                )

                # ---- Industry enrichment
                broker_record["industry_focus"] = (
                    broker_data.get("industry_focus")
                    or broker_record["industry_focus"]
                )

            except Exception as e:
                print(f"  ⚠ Deep extraction error: {str(e)[:60]}")

            # ---------------- VALIDATION ----------------
            has_contact = broker_record.get("email") or broker_record.get("phone")
            has_name = broker_record.get("broker_name") not in ["Not Available", "", None]

            if has_contact or has_name:
                extracted.append(broker_record)
                processed += 1
                print("  ✅ Added to Broker Database")
            else:
                print("  ⚠ Skipped: No useful broker data")

            random_delay()

        except Exception as e:
            print(f"  ❌ Failed listing: {str(e)[:80]}")

    # ---------------- FINAL STATE UPDATE ----------------
    state["broker_database"] = extracted
    state["processed_count"] = processed
    state["current_stage"] = "extraction_complete"

    print(f"\n📊 Extraction Complete: {processed} brokers ready for CSV.")
    return state
