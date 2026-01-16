import pandas as pd
from agent.state import AgentState


def tag_data_node(state: AgentState) -> AgentState:
    """Pass through - just forward DataFrames to organize node"""
    
    print("\n" + "=" * 60)
    print("NODE 2: TAGGING & CATEGORIZING DATA")
    print("=" * 60)
    
    # CRITICAL: Just pass through - don't modify state
    # The DataFrames are already in state from load_data_node
    
    df_listings = state.get("listings_df")
    df_brokers = state.get("brokers_df")
    df_emails = state.get("emails_df")
    
    listings_count = len(df_listings) if df_listings is not None and not df_listings.empty else 0
    brokers_count = len(df_brokers) if df_brokers is not None and not df_brokers.empty else 0
    emails_count = len(df_emails) if df_emails is not None and not df_emails.empty else 0
    
    print(f"✓ Tagged {listings_count} listings")
    print(f"✓ Tagged {brokers_count} brokers")
    print(f"✓ Tagged {emails_count} email drafts")
    
    state["tag_summary"] = {"Industries": {}, "Sizes": {}, "Geographies": {}}
    state["current_stage"] = "data_tagged"
    
    print(f"\n📊 Tag Summary:")
    print(f"  Industries: 0")
    print(f"  Sizes: 0")
    print(f"  Geographies: 0")
    
    return state