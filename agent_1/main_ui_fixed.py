#!/usr/bin/env python3
import sys
import os
from pathlib import Path
import pandas as pd
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from config import SCRAPING_CONFIG, OUTPUT_CONFIG
from scrapers.bizbuysell import scrape_bizbuysell
from scrapers.bizquest import scrape_bizquest
from scrapers.loopnet import scrape_loopnet

def main():
    """Run Agent 1: Multi-Website Listing Scraper"""
    print("\n" + "="*70)
    print("Agent 1: BUSINESS LISTING SCRAPER")
    print("="*70)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    # Get number of listings from environment or use config default
    num_listings = int(os.environ.get('NUM_LISTINGS', str(SCRAPING_CONFIG['bizbuysell']['max_listings'])))
    
    # Update config with environment variable
    SCRAPING_CONFIG["bizbuysell"]["max_listings"] = num_listings
    SCRAPING_CONFIG["bizquest"]["max_listings"] = num_listings
    SCRAPING_CONFIG["loopnet"]["max_listings"] = num_listings
    
    # Print configuration
    print("\nScraping Configuration:")
    for website, config in SCRAPING_CONFIG.items():
        if config["enabled"]:
            print(f"  {website.upper()}: {config['max_listings']} listings (max {config['max_pages']} pages)")
        else:
            print(f"  {website.upper()}: Disabled")
    
    all_listings = []
    
    # ==================== BizBuySell ====================
    if SCRAPING_CONFIG["bizbuysell"]["enabled"]:
        print("\n" + "="*70)
        print("SOURCE 1: BizBuySell")
        print("="*70)
        try:
            bizbuysell_listings = scrape_bizbuysell(
                max_listings=SCRAPING_CONFIG["bizbuysell"]["max_listings"],
                max_pages=SCRAPING_CONFIG["bizbuysell"]["max_pages"]
            )
            all_listings.extend(bizbuysell_listings)
            print(f"BizBuySell Complete: {len(bizbuysell_listings)} listings scraped")
            
            # Save intermediate
            if OUTPUT_CONFIG["save_intermediate"]:
                save_intermediate(bizbuysell_listings, "bizbuysell")
                
        except Exception as e:
            print(f"BizBuySell Failed: {e}")
    
    # ==================== BizQuest ====================
    if SCRAPING_CONFIG["bizquest"]["enabled"]:
        print("\n" + "="*70)
        print("SOURCE 2: BizQuest")
        print("="*70)
        try:
            bizquest_listings = scrape_bizquest(
                max_listings=SCRAPING_CONFIG["bizquest"]["max_listings"],
                max_pages=SCRAPING_CONFIG["bizquest"]["max_pages"]
            )
            all_listings.extend(bizquest_listings)
            print(f"BizQuest Complete: {len(bizquest_listings)} listings scraped")
            
            # Save intermediate
            if OUTPUT_CONFIG["save_intermediate"]:
                save_intermediate(bizquest_listings, "bizquest")
                
        except Exception as e:
            print(f"BizQuest Failed: {e}")
    
    # ==================== LoopNet ====================
    if SCRAPING_CONFIG["loopnet"]["enabled"]:
        print("\n" + "="*70)
        print("SOURCE 3: LoopNet")
        print("="*70)
        try:
            loopnet_listings = scrape_loopnet(
                max_listings=SCRAPING_CONFIG["loopnet"]["max_listings"],
                max_pages=SCRAPING_CONFIG["loopnet"]["max_pages"]
            )
            all_listings.extend(loopnet_listings)
            print(f"LoopNet Complete: {len(loopnet_listings)} listings scraped")
            
            # Save intermediate
            if OUTPUT_CONFIG["save_intermediate"]:
                save_intermediate(loopnet_listings, "loopnet")
                
        except Exception as e:
            print(f"LoopNet Failed: {e}")
    
    # ==================== Save Final Output ====================
    if all_listings:
        df = pd.DataFrame(all_listings)
        
        # Create output directory
        output_path = Path(__file__).parent / OUTPUT_CONFIG["output_file"]
        output_path.parent.mkdir(exist_ok=True)
        
        # Save CSV
        df.to_csv(output_path, index=False)
        
        # Print summary
        print("\n" + "="*70)
        print("AGENT 1 EXECUTION COMPLETE")
        print("="*70)
        print(f"\nFinal Statistics:")
        print(f"  Total Listings: {len(all_listings)}")
        
        for source in ["BizBuySell", "BizQuest", "LoopNet"]:
            count = len([l for l in all_listings if l.get('Source') == source])
            print(f"  - {source}: {count} listings")
        
        print(f"\nOutput File: {output_path}")
        print(f"File Size: {output_path.stat().st_size / 1024:.2f} KB")
        print("="*70)
        
        return all_listings
    else:
        print("\nWARNING: No listings scraped from any source")
        return []


def save_intermediate(listings, source_name):
    """Save intermediate CSV for each website"""
    if not listings:
        return
    
    df = pd.DataFrame(listings)
    output_path = Path(__file__).parent / f"output/{source_name}_listings.csv"
    output_path.parent.mkdir(exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"  Intermediate saved: {output_path}")


if __name__ == "__main__":
    main()