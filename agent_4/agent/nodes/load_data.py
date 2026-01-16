import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agent.state import AgentState
from config.settings import LISTINGS_CSV, BROKERS_CSV, EMAILS_CSV


def load_data_node(state: AgentState) -> AgentState:
    """Load and normalize data from all agents"""

    print("\n" + "="*60)
    print("NODE 1: LOADING DATA FROM ALL AGENTS")
    print("="*60)

    # -----------------------
    # Agent 1: Listings
    # -----------------------
    try:
        df_listings = pd.read_csv(LISTINGS_CSV)
        # Normalize column names
        df_listings.columns = df_listings.columns.str.strip()
        state["listings_df"] = df_listings
        print(f"✓ Loaded {len(df_listings)} listings from Agent 1")
    except Exception as e:
        state["errors"].append(f"Failed to load listings: {str(e)}")
        state["listings_df"] = pd.DataFrame()

    # -----------------------
    # Agent 2: Brokers
    # -----------------------
    try:
        df_brokers = pd.read_csv(BROKERS_CSV)
        # Normalize column names
        df_brokers.columns = df_brokers.columns.str.strip()
        # Standardize email column
        if "Email" in df_brokers.columns:
            df_brokers["broker_email"] = df_brokers["Email"]
        elif "email" in df_brokers.columns:
            df_brokers["broker_email"] = df_brokers["email"]
        state["brokers_df"] = df_brokers
        print(f"✓ Loaded {len(df_brokers)} brokers from Agent 2")
    except Exception as e:
        state["errors"].append(f"Failed to load brokers: {str(e)}")
        state["brokers_df"] = pd.DataFrame()

    # -----------------------
    # Agent 3: Email Drafts
    # -----------------------
    try:
        df_emails = pd.read_csv(EMAILS_CSV)
        df_emails.columns = df_emails.columns.str.strip()
        state["emails_df"] = df_emails
        print(f"✓ Loaded {len(df_emails)} email drafts from Agent 3")
    except Exception as e:
        state["errors"].append(f"Failed to load emails: {str(e)}")
        state["emails_df"] = pd.DataFrame()

    # Calculate totals
    total = len(state.get("listings_df", pd.DataFrame())) + \
            len(state.get("brokers_df", pd.DataFrame())) + \
            len(state.get("emails_df", pd.DataFrame()))
    
    state["total_records"] = total
    state["current_stage"] = "data_loaded"

    print(f"\n✓ Total catalog records: {total}")

    return state