import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agent.state import AgentState
from config.settings import BROKER_DATABASE_CSV, EMAIL_CONFIG


def load_brokers_node(state: AgentState) -> AgentState:
    """Load broker database from Agent 2"""
    
    print("\n" + "="*60)
    print("NODE 1: LOADING BROKER DATABASE")
    print("="*60)
    
    try:
        df = pd.read_csv(BROKER_DATABASE_CSV)
        print(f"✓ Loaded {len(df)} brokers from database")
    except Exception as e:
        state["errors"].append(f"Failed to load database: {str(e)}")
        return state
    
    # Convert to list
    brokers = df.to_dict('records')
    
    # CHANGED: Don't skip brokers without email
    brokers_with_email = []
    brokers_need_lookup = []
    
    for b in brokers:
        email = b.get('email')
        # Check if valid email exists
        if email and pd.notna(email) and str(email) != 'nan' and '@' in str(email):
            brokers_with_email.append(b)
        else:
            # Add placeholder for manual lookup
            broker_name = b.get('broker_name', 'Unknown')
            broker_firm = b.get('brokerage_firm', 'Unknown')
            b['email'] = f"[LOOKUP: {broker_name} @ {broker_firm}]"
            brokers_need_lookup.append(b)
    
    all_brokers = brokers_with_email + brokers_need_lookup
    
    print(f"✓ Brokers with email: {len(brokers_with_email)}")
    print(f"⚠ Brokers needing email lookup: {len(brokers_need_lookup)}")
    print(f"✓ Total emails to generate: {len(all_brokers)}")
    
    # Apply limit
    max_emails = EMAIL_CONFIG["max_emails_per_run"]
    if len(all_brokers) > max_emails:
        print(f"⚠ Limiting to {max_emails} brokers")
        all_brokers = all_brokers[:max_emails]
    
    state["broker_database"] = all_brokers
    state["total_brokers"] = len(all_brokers)
    state["current_stage"] = "brokers_loaded"
    
    print(f"✓ Ready to generate {len(all_brokers)} email drafts")
    
    return state