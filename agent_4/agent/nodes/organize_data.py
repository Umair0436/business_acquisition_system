import pandas as pd
import uuid
from agent.state import AgentState


def safe_str(value) -> str:
    """Convert NaN / None / float to safe string"""
    if value is None or pd.isna(value):
        return ""
    if isinstance(value, float):
        return ""
    return str(value).strip()


def organize_data_node(state: AgentState) -> AgentState:
    """Merge listings + brokers + emails into SINGLE ROWS"""

    print("\n" + "=" * 60)
    print("NODE 3: ORGANIZING & MERGING DATA")
    print("=" * 60)

    # Get DataFrames from state
    df_listings = state.get("listings_df", pd.DataFrame())
    df_brokers = state.get("brokers_df", pd.DataFrame())
    df_emails = state.get("emails_df", pd.DataFrame())

    master_records = []
    processed_urls = set()

    # -----------------------
    # ONE ROW PER LISTING (with broker + email merged)
    # -----------------------
    for idx, row in df_listings.iterrows():
        listing_url = safe_str(row.get("Listing URL"))
        
        if listing_url in processed_urls:
            continue
        processed_urls.add(listing_url)
        
        # Initialize record with listing data
        record = {
            "record_id": f"listing_{uuid.uuid4().hex[:16]}",
            "record_type": "listing",
            "business_name": safe_str(row.get("Business Name")),
            "industry_tag": safe_str(row.get("Industry")),
            "geography_tag": safe_str(row.get("Location")),
            "size_tag": "",
            "deal_status": "Active",
            "broker_name": "",
            "broker_email": "",
            "broker_phone": "",
            "brokerage_firm": "",
            "broker_linkedin": "",
            "email_subject": "",
            "email_body": "",
            "email_tone": "",
            "raw_data": {
                "Business Name": safe_str(row.get("Business Name")),
                "Industry": safe_str(row.get("Industry")),
                "Location": safe_str(row.get("Location")),
                "Asking Price": safe_str(row.get("Asking Price")),
                "Revenue": safe_str(row.get("Revenue")),
                "EBITDA": safe_str(row.get("EBITDA")),
                "Years in Operation": safe_str(row.get("Years in Operation")),
                "Listing URL": listing_url,
                "Source": safe_str(row.get("Source")),
                "Broker or Seller Contact": safe_str(row.get("Broker or Seller Contact"))
            }
        }
        
        # STEP 1: Merge Broker Data (by Listing URL)
        if not df_brokers.empty and listing_url and "source_listing_url" in df_brokers.columns:
            broker_match = df_brokers[df_brokers["source_listing_url"] == listing_url]
            if not broker_match.empty:
                broker = broker_match.iloc[0]
                record["broker_name"] = safe_str(broker.get("broker_name"))
                record["broker_email"] = safe_str(broker.get("email"))
                record["broker_phone"] = safe_str(broker.get("phone"))
                record["brokerage_firm"] = safe_str(broker.get("brokerage_firm"))
                record["broker_linkedin"] = safe_str(broker.get("linkedin_search_url"))
                
                # Update industry/geography from broker if listing doesn't have it
                if not record["industry_tag"] or record["industry_tag"] == "Not Specified":
                    record["industry_tag"] = safe_str(broker.get("industry_focus"))
                if not record["geography_tag"] or record["geography_tag"] == "Not Specified":
                    record["geography_tag"] = safe_str(broker.get("geography"))
                
                # Update raw_data
                record["raw_data"].update({
                    "brokerage_firm": record["brokerage_firm"],
                    "email": record["broker_email"],
                    "phone": record["broker_phone"],
                    "linkedin_search_url": record["broker_linkedin"]
                })
        
        # STEP 2: Merge Email Data (by broker email)
        if record["broker_email"] and not df_emails.empty and "broker_email" in df_emails.columns:
            email_match = df_emails[df_emails["broker_email"].str.lower() == record["broker_email"].lower()]
            if not email_match.empty:
                email = email_match.iloc[0]
                record["email_subject"] = safe_str(email.get("email_subject"))
                record["email_body"] = safe_str(email.get("email_body"))
                record["email_tone"] = safe_str(email.get("tone"))
                
                record["raw_data"].update({
                    "email_subject": record["email_subject"],
                    "email_body": record["email_body"],
                    "email_tone": record["email_tone"]
                })
        
        master_records.append(record)

    state["catalog_records"] = master_records
    state["current_stage"] = "data_organized"

    print(f"✓ Organized {len(master_records)} merged records")
    print(f"  - Each row contains: Listing + Broker + Email data")
    print("✓ Single row per business")

    return state