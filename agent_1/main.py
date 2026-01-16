#!/usr/bin/env python3
import sys
from pathlib import Path
import pandas as pd
from datetime import datetime

# ✅ Fix Unicode issue on Windows
sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).parent))

# ========== SMART INPUT HANDLING ==========
print("\n" + "="*50)
print("⚙️  SCRAPING CONFIGURATION")
print("="*50)

# Try to get from config first (dashboard mode), else ask for input
try:
    from config import NUM_LISTINGS
    print(f"✓ Using dashboard configuration: {NUM_LISTINGS} listings per website")
except ImportError:
    # Fallback to interactive mode (manual execution)
    num_listings = input("How many listings per website? [10]: ").strip()
    if num_listings.isdigit():
        NUM_LISTINGS = int(num_listings)
    else:
        NUM_LISTINGS = 10
    print(f"✓ Will scrape {NUM_LISTINGS} listings from each website")
# ========================================

# Import config and scraper functions
from config import SCRAPING_CONFIG, OUTPUT_CONFIG
from scrapers.bizbuysell import scrape_bizbuysell
from scrapers.bizquest import scrape_bizquest
from scrapers.loopnet import scrape_loopnet

# Update config with user input dynamically
for scraper_name, scraper_cfg in SCRAPING_CONFIG.items():
    if isinstance(scraper_cfg, dict):
        scraper_cfg["max_listings"] = NUM_LISTINGS


def save_intermediate(listings, source_name):
    """Save intermediate CSV for each website"""
    if not listings:
        return
    
    df = pd.DataFrame(listings)
    output_path = Path(__file__).parent / f"output/{source_name}_listings.csv"
    output_path.parent.mkdir(exist_ok=True)
    df.to_csv(output_path, index=False, encoding='utf-8')
    print(f"  💾 Intermediate saved: {output_path}")


def main():
    """Run Agent 1: Multi-Website Listing Scraper"""
    print("\n" + "="*70)
    print("🤖 AGENT 1: BUSINESS LISTING SCRAPER")
    print("="*70)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    # Show scraping configuration
    print("\n📋 Scraping Configuration:")
    for website, config in SCRAPING_CONFIG.items():
        if config.get("enabled", False):
            max_pages = config.get('max_pages', 10)
            print(f"  ✓ {website.upper()}: {config['max_listings']} listings (max {max_pages} pages)")
        else:
            print(f"  ✗ {website.upper()}: Disabled")
    
    all_listings = []

    # Dynamic scraper function mapping
    SCRAPER_FUNCTIONS = {
        "bizbuysell": scrape_bizbuysell,
        "biz_buy_sell": scrape_bizbuysell,
        "bizquest": scrape_bizquest,
        "loopnet": scrape_loopnet,
        "loop_net": scrape_loopnet
    }

    # Loop through all configured scrapers
    for scraper_name, scraper_cfg in SCRAPING_CONFIG.items():
        if not scraper_cfg.get("enabled", False):
            print(f"\n✗ {scraper_name.upper()} is disabled")
            continue
        
        print("\n" + "="*70)
        print(f"📍 SOURCE: {scraper_name.upper()}")
        print("="*70)
        
        func = SCRAPER_FUNCTIONS.get(scraper_name)
        if not func:
            print(f"⚠ No scraper function found for {scraper_name}")
            continue
        
        try:
            max_pages = scraper_cfg.get("max_pages", 10)
            listings = func(
                max_listings=scraper_cfg["max_listings"],
                max_pages=max_pages
            )
            all_listings.extend(listings)
            print(f"✅ {scraper_name.upper()} Complete: {len(listings)} listings scraped")
            
            # Save intermediate CSV
            if OUTPUT_CONFIG.get("save_intermediate", False):
                save_intermediate(listings, scraper_name)
        
        except Exception as e:
            print(f"❌ {scraper_name.upper()} Failed: {e}")

    # ==================== Save final output ====================
    if all_listings:
        df = pd.DataFrame(all_listings)
        
        output_path = Path(__file__).parent / OUTPUT_CONFIG.get("output_file", "output/listings.csv")
        output_path.parent.mkdir(exist_ok=True)
        df.to_csv(output_path, index=False, encoding='utf-8')
        
        # Summary
        print("\n" + "="*70)
        print("✅ AGENT 1 EXECUTION COMPLETE")
        print("="*70)
        print(f"\n📊 Final Statistics:")
        print(f"  Total Listings: {len(all_listings)}")
        
        # Count per source
        for source in SCRAPER_FUNCTIONS.keys():
            count = len([l for l in all_listings if l.get('Source', '').lower() == source.lower()])
            if count > 0:
                print(f"  - {source}: {count} listings")
        
        print(f"\n📁 Output File: {output_path}")
        print(f"📏 File Size: {output_path.stat().st_size / 1024:.2f} KB")
        print("="*70)
        return all_listings
    else:
        print("\n⚠ WARNING: No listings scraped from any source")
        return []


if __name__ == "__main__":
    main()