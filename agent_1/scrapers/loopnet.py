from seleniumbase import SB
import re
import time
import random


def normalize_money(text):
    """Convert price text to number"""
    if not text:
        return 0
    text = str(text).lower().replace('$', '').replace(',', '').strip()
    if any(w in text for w in ['disclosed', 'n/a', 'none', 'call']):
        return 0
    mult = 1_000_000 if 'm' in text else 1_000 if 'k' in text else 1
    text = text.replace('m', '').replace('k', '')
    match = re.search(r'[\d.]+', text)
    return int(float(match.group()) * mult) if match else 0


def find_value(keyword, text):
    """Find price values in text"""
    for pattern in [rf"{keyword}[:\s]*(\$[\d,KkMm.]+)", rf"{keyword}.*?(\$[\d,KkMm.]+)"]:
        match = re.search(pattern, text, re.I)
        if match:
            return match.group(1)
    return None


def scrape_loopnet(max_listings=5, max_pages=3):
    """
    Scrape LoopNet listings
    Args:
        max_listings: Number of listings to scrape
        max_pages: Not used (for compatibility)
    """
    print(f"Target: {max_listings} listings")
    
    results = []
    
    with SB(uc=True, headless=False) as sb:
        # Get listing URLs
        url = "https://www.loopnet.com/search/commercial-real-estate/for-sale/"
        print(f"\nLoopNet: Getting {max_listings} links...")
        
        try:
            sb.uc_open_with_reconnect(url, reconnect_time=10)
            sb.sleep(random.uniform(3, 5))
            
            # Scroll to load content
            for i in range(5):
                sb.execute_script(f"window.scrollTo(0, {1000*(i+1)});")
                sb.sleep(1)
            
            # Find links
            links = []
            all_links = sb.find_elements("a")
            for elem in all_links:
                try:
                    href = elem.get_attribute("href")
                    if href and "loopnet.com" in href and "/Listing/" in href:
                        if href not in links:
                            links.append(href)
                            print(f"      Found: {href[:60]}...")
                            if len(links) >= max_listings:
                                break
                except:
                    continue
            
            print(f"   Found {len(links)} links")
            
            # Scrape each listing
            for i, listing_url in enumerate(links, 1):
                print(f"[LoopNet {i}/{len(links)}]")
                try:
                    sb.uc_open_with_reconnect(listing_url, reconnect_time=10)
                    sb.sleep(random.uniform(2, 4))
                    
                    body = sb.get_text("body")
                    
                    # Extract title
                    title = "LoopNet Listing"
                    if sb.is_element_present("h1"):
                        title = sb.get_text("h1")
                    
                    # Extract prices
                    asking = find_value("price", body)
                    revenue = find_value("revenue", body)
                    cashflow = find_value("net", body)
                    
                    data = {
                        "Business Name": title.strip(),
                        "Industry": "Real Estate",
                        "Location": "Not Specified",
                        "Asking Price": normalize_money(asking),
                        "Revenue": normalize_money(revenue),
                        "EBITDA": normalize_money(cashflow),
                        "Years in Operation": "Not Disclosed",
                        "Broker or Seller Contact": "Not Available",
                        "Listing URL": listing_url,
                        "Source": "LoopNet",
                    }
                    
                    results.append(data)
                    
                    time.sleep(random.uniform(3, 6))
                    
                except Exception as e:
                    print(f"   ⚠️ Error: {str(e)[:50]}")
                    continue
        
        except Exception as e:
            print(f"❌ LoopNet search failed: {str(e)}")
    
    print(f"LoopNet Complete: {len(results)} listings scraped")
    return results