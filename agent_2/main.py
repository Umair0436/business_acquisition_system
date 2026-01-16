#!/usr/bin/env python3
import sys
import os
import pandas as pd
from pathlib import Path
from datetime import datetime

# ======================================================================
# 🛠️ CRITICAL PATH FIX (For LangGraph & Pipeline)
# ======================================================================
base_dir = os.path.dirname(os.path.abspath(__file__))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

# Imports path fix ke baad
from agent.graph import create_broker_intelligence_graph
from agent.state import AgentState
from config.settings import OUTPUT_CSV

def load_input_data(file_path):
    """Pipeline se aayi hui listings.csv load karein aur columns check karein"""
    print(f"🔍 Checking file: {file_path}")
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        try:
            # Encoding UTF-8-SIG taake Excel/CSV ke hidden characters masla na karein
            df = pd.read_csv(file_path, encoding='utf-8-sig')
            
            # Agar Agent 1 ne data nikala hai toh column names clean karein
            df.columns = [c.strip() for c in df.columns]
            
            print(f"✅ Columns found: {list(df.columns)}")
            return df.to_dict('records')
        except Exception as e:
            print(f"❌ Error reading CSV: {e}")
    else:
        print("⚠ Warning: listings.csv is missing or empty!")
    return []

def main():
    """Run Broker Intelligence Agent"""
    
    print("\n" + "="*70)
    print("🤖 LANGGRAPH: BUSINESS BROKER INTELLIGENCE AGENT")
    print("="*70)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Path setup: Agent 2 ke input folder se file uthana
    input_file = os.path.join(base_dir, "input", "listings.csv")
    listings = load_input_data(input_file)
    
    print(f"📂 Data Loaded: {len(listings)} listings ready for LangGraph.")
    print("="*70)

    # Initial State for LangGraph
    initial_state: AgentState = {
        "input_listings": listings,
        "listings_to_process": listings,
        "current_index": 0,
        "total_listings": len(listings),
        "broker_database": [],
        "processed_count": 0,
        "skipped_count": 0,
        "errors": [],
        "current_stage": "start",
        "output_path": str(OUTPUT_CSV)
    }
    
    # LangGraph Initialize
    app = create_broker_intelligence_graph()
    
    try:
        if not listings:
            print("❌ No data to process. Agent 2 stopping.")
            return None

        # Start LangGraph Execution
        final_state = app.invoke(initial_state)
        
        print("\n" + "="*70)
        print("✅ LANGGRAPH EXECUTION COMPLETE")
        print("="*70)
        print(f"📊 Final Results for Client Video:")
        print(f" - Total Listings: {final_state['total_listings']}")
        print(f" - Brokers Successfully Extracted: {final_state['processed_count']}")
        print(f"📂 Master Database: {final_state['output_path']}")
        print("="*70)
        
        return final_state
        
    except Exception as e:
        print(f"\n❌ FATAL ERROR IN GRAPH: {str(e)}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    main()