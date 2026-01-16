#!/usr/bin/env python3
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from agent.graph import create_email_outreach_graph
from agent.state import AgentState
from config.settings import EMAIL_DRAFTS_CSV, AVAILABLE_TONES
from dotenv import load_dotenv
load_dotenv()


def main():
    """Run Email Outreach Agent"""
    
    print("\n" + "="*70)
    print("📧 EMAIL DRAFTING & OUTREACH AGENT")
    print("="*70)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    # Interactive tone selection
    print("\n📋 Select Email Tone:")
    for key, desc in AVAILABLE_TONES.items():
        print(f"  {key[0].upper()}. {desc}")
    
    tone_input = input("\nEnter tone (p/r/d) [p]: ").strip().lower()
    
    tone_map = {
        'p': 'professional',
        'r': 'relationship',
        'd': 'direct',
        '': 'professional'
    }
    
    selected_tone = tone_map.get(tone_input, 'professional')
    
    print(f"\n✓ Selected: {AVAILABLE_TONES[selected_tone]}")
    
    # Initialize state
    initial_state: AgentState = {
        "broker_database": [],
        "selected_tone": selected_tone,
        "email_drafts": [],
        "total_brokers": 0,
        "drafts_generated": 0,
        "errors": [],
        "current_stage": "initialized",
        "output_path": str(EMAIL_DRAFTS_CSV)
    }
    
    # Create and run graph
    app = create_email_outreach_graph()
    
    try:
        final_state = app.invoke(initial_state)
        
        # Print summary
        print("\n" + "="*70)
        print("✅ AGENT EXECUTION COMPLETE")
        print("="*70)
        print(f"Total Brokers Loaded: {final_state['total_brokers']}")
        print(f"Drafts Generated: {final_state['drafts_generated']}")
        print(f"Errors: {len(final_state['errors'])}")
        print(f"\nOutput: {final_state['output_path']}")
        
        if final_state['errors']:
            print("\n⚠ Errors:")
            for error in final_state['errors'][:5]:
                print(f"  - {error}")
        
        print("="*70)
        
        return final_state
        
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {str(e)}")
        raise


if __name__ == "__main__":
    main()