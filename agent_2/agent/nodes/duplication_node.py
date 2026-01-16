from typing import List
import sys
import os
from pathlib import Path

# ======================================================================
# 🛠️ UNIVERSAL PATH FIX
# ======================================================================
current_file = os.path.abspath(__file__)
agent2_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))

if agent2_root not in sys.path:
    sys.path.insert(0, agent2_root)

from agent.state import AgentState, BrokerRecord

try:
    from utils.validators import normalize_name, normalize_firm
except ImportError:
    from agent_2.utils.validators import normalize_name, normalize_firm


def deduplicate_brokers_node(state: AgentState) -> AgentState:
    print("\n" + "="*60)
    print("NODE 3: DEDUPLICATION & UPSERT")
    print("="*60)
    
    extracted_brokers = state["broker_database"]
    
    if not extracted_brokers:
        print("⚠ No brokers")
        state["current_stage"] = "deduplication_complete"
        return state
    
    unique_brokers = []  # Fresh list
    
    for broker in extracted_brokers:
        norm_name = normalize_name(broker["broker_name"])
        
        # Skip bad names
        if not norm_name or norm_name.lower() in ['not available', 'not availabl']:
            continue
        
        # Check duplicate
        is_dup = False
        for existing in unique_brokers:
            if normalize_name(existing["broker_name"]) == norm_name:
                is_dup = True
                break
        
        if not is_dup:
            unique_brokers.append(broker)
    
    # CRITICAL: Replace, don't append!
    state["broker_database"] = unique_brokers  # ← THIS LINE
    state["current_stage"] = "deduplication_complete"
    
    print(f"✓ Unique Entries: {len(unique_brokers)}")
    return state