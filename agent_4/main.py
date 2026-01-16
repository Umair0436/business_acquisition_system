#!/usr/bin/env python3
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from agent.graph import create_catalog_graph
from agent.state import AgentState


def main():
    """Run Data Catalog Agent"""
    
    print("\n" + "="*70)
    print("📂 DATA FILING & CATALOGING AGENT")
    print("="*70)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    # Initialize state
    initial_state: AgentState = {
    "listings_df": None,      # ← CORRECT
    "brokers_df": None,       # ← CORRECT
    "emails_df": None,        # ← CORRECT
    "catalog_records": [],
    "tag_summary": {},
    "total_records": 0,
    "errors": [],
    "current_stage": "initialized",
    "output_paths": {}
}
    
    # Create and run graph
    app = create_catalog_graph()
    
    try:
        final_state = app.invoke(initial_state)
        
        # Print summary
        print("\n" + "="*70)
        print("✅ AGENT EXECUTION COMPLETE")
        print("="*70)
        print(f"Total Records Cataloged: {final_state['total_records']}")
        print(f"Errors: {len(final_state['errors'])}")
        
        print(f"\n📊 Tag Summary:")
        summary = final_state.get('tag_summary', {})
        
        if summary.get('by_industry'):
            print(f"\n  Industries:")
            for ind, count in sorted(summary['by_industry'].items(), key=lambda x: -x[1])[:5]:
                print(f"    - {ind}: {count}")
        
        if summary.get('by_size'):
            print(f"\n  Sizes:")
            for size, count in summary['by_size'].items():
                print(f"    - {size}: {count}")
        
        if summary.get('by_geography'):
            print(f"\n  Top Geographies:")
            for geo, count in sorted(summary['by_geography'].items(), key=lambda x: -x[1])[:5]:
                print(f"    - {geo}: {count}")
        
        print(f"\n📁 Output Files:")
        for format_name, path in final_state.get('output_paths', {}).items():
            print(f"  - {format_name.upper()}: {path}")
        
        if final_state['errors']:
            print("\n⚠ Errors:")
            for error in final_state['errors']:
                print(f"  - {error}")
        
        print("="*70)
        
        return final_state
        
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {str(e)}")
        raise


if __name__ == "__main__":
    main()