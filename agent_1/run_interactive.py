import sys
from pathlib import Path

# Fix path
agent2_root = Path(__file__).resolve().parent.parent.parent
if str(agent2_root) not in sys.path:
    sys.path.insert(0, str(agent2_root))

from datetime import datetime
from graph.state import AgentState, BrokerRecord
from agent_2.utils.scraper import BrokerScraper, random_delay


def deep_extraction_node(state: AgentState) -> AgentState:
    # ... rest same
    """Interactive configuration for scraping"""
    print("\n" + "="*70)
    print("⚙️  INTERACTIVE SCRAPING CONFIGURATION")
    print("="*70)
    
    for website in ["bizbuysell", "bizquest", "loopnet"]:
        print(f"\n📌 {website.upper()}")
        
        # Enable/Disable
        enabled = input(f"  Enable {website}? (y/n) [y]: ").strip().lower()
        SCRAPING_CONFIG[website]["enabled"] = enabled != 'n'
        
        if SCRAPING_CONFIG[website]["enabled"]:
            # Max listings
            max_listings = input(f"  Max listings? [{SCRAPING_CONFIG[website]['max_listings']}]: ").strip()
            if max_listings.isdigit():
                SCRAPING_CONFIG[website]["max_listings"] = int(max_listings)
            
            # Max pages
            max_pages = input(f"  Max pages? [{SCRAPING_CONFIG[website]['max_pages']}]: ").strip()
            if max_pages.isdigit():
                SCRAPING_CONFIG[website]["max_pages"] = int(max_pages)
    
    print("\n" + "="*70)
    print("✅ Configuration Complete")
    print("="*70)
    
    # Confirm
    confirm = input("\nStart scraping? (y/n) [y]: ").strip().lower()
    if confirm == 'n':
        print("❌ Cancelled")
        return
    
    # Run main
    main()


if __name__ == "__main__":
    configure_interactive()