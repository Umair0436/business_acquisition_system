import pandas as pd
from typing import Dict, List
import sys
from pathlib import Path

# Fix imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agent.state import AgentState
from config.settings import INPUT_CSV, FORM_KEYWORDS


def filter_listings_node(state: AgentState) -> AgentState:
    """Filter listings that need deep extraction"""
    
    print("\n" + "="*60)
    print("NODE 1: FILTERING LISTINGS")
    print("="*60)
    
    try:
        df = pd.read_csv(INPUT_CSV)
        print(f"✓ Loaded {len(df)} listings from CSV")
    except Exception as e:
        state["errors"].append(f"Failed to read CSV: {str(e)}")
        return state
    
    all_listings = df.to_dict('records')
    state["input_listings"] = all_listings
    
    listings_to_process = []
    
    for listing in all_listings:
        broker_contact = str(listing.get('Broker Contact', '')).lower()
        
        needs_extraction = any(keyword in broker_contact for keyword in FORM_KEYWORDS)
        
        if needs_extraction or broker_contact in ['', 'nan', 'none', 'n/a']:
            listings_to_process.append(listing)
    
    state["listings_to_process"] = listings_to_process
    state["total_listings"] = len(listings_to_process)
    state["current_stage"] = "filtering_complete"
    
    print(f"✓ {len(listings_to_process)} listings need deep extraction")
    print(f"✓ {len(all_listings) - len(listings_to_process)} listings have valid broker info")
    
    return state