#!/usr/bin/env python3
import sys
from pathlib import Path
import pandas as pd
from datetime import datetime
import random

sys.path.insert(0, str(Path(__file__).parent))

def create_sample_listings(num_listings):
    """Create sample listings for testing"""
    sources = ["BizBuySell", "BizQuest", "LoopNet"]
    industries = ["Restaurant", "Retail", "Manufacturing", "Technology", "Healthcare", "Construction"]
    states = ["CA", "NY", "TX", "FL", "IL", "WA"]
    
    listings = []
    for i in range(num_listings):
        source = random.choice(sources)
        listings.append({
            'title': f'Sample Business {i+1}',
            'price': f'${random.randint(100000, 5000000):,}',
            'industry': random.choice(industries),
            'location': f'{random.choice(states)}, USA',
            'Source': source,
            'url': f'https://example.com/business-{i+1}',
            'description': f'Sample description for business {i+1} in {random.choice(industries)} industry.',
            'revenue': f'${random.randint(500000, 10000000):,}',
            'cash_flow': f'${random.randint(50000, 1000000):,}'
        })
    
    return listings

def main():
    """Run Agent 1: Business Listing Scraper"""
    print("\n" + "="*70)
    print("Agent 1: BUSINESS LISTING SCRAPER (TEST MODE)")
    print("="*70)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    # Get number of listings from environment or use default
    num_listings = int(os.environ.get('NUM_LISTINGS', '15'))
    print(f"Generating {num_listings} sample listings for testing...")
    
    # Create sample listings
    all_listings = create_sample_listings(num_listings)
    
    if all_listings:
        df = pd.DataFrame(all_listings)
        
        # Create output directory
        output_path = Path(__file__).parent / "output" / "listings.csv"
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
        print("\nWARNING: No listings generated")
        return []

if __name__ == "__main__":
    import os
    main()