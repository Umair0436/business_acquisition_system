from seleniumbase import SB
import pandas as pd
import re
import os
from datetime import datetime

# ====================== UTILS ====================== #

def normalize_money(text):
    if not text:
        return 0
    text = str(text).lower().replace('$', '').replace(',', '').strip()
    if any(w in text for w in ['disclosed', 'n/a', 'not disclosed']):
        return 0

    mult = 1
    if 'm' in text:
        mult = 1_000_000
    elif 'k' in text:
        mult = 1_000

    text = text.replace('m', '').replace('k', '')
    match = re.search(r'[\d.]+', text)
    return int(float(match.group()) * mult) if match else 0


def find_value(keyword, text):
    patterns = [
        rf"{keyword}[:\s]*(\$[\d,KkMm.]+)",
        rf"{keyword}.*?(\$[\d,KkMm.]+)"
    ]
    for p in patterns:
        m = re.search(p, text, re.I)
        if m:
            return m.group(1)
    return None


# ================== LINK COLLECTOR ================= #

def get_links_bizbuysell(sb, max_count):
    url = "https://www.bizbuysell.com/recent-listings-for-sale/"
    print(f"\nBizBuySell: collecting {max_count} links")

    sb.uc_open_with_reconnect(url, reconnect_time=2)

    # ✅ FLEXIBLE WAIT (robust against layout / lazy load)
    sb.wait_for_element("body", timeout=10)
    sb.sleep(3)

    links = []

    # Multiple passes because BizBuySell lazy-loads
    for _ in range(3):
        elements = sb.find_elements("a[href*='/business-opportunity/']")
        for el in elements:
            href = el.get_attribute("href")
            if href and href not in links:
                links.append(href)
            if len(links) >= max_count:
                break

        if len(links) >= max_count:
            break

        sb.sleep(2)

    print(f"   Collected {len(links)} links")
    return links


# ================== DETAIL SCRAPER ================= #

def scrape_bizbuysell(max_listings=10, max_pages=3):
    print(f"Target: {max_listings} listings from {max_pages} pages")
    results = []

    with SB(uc=True, headless=False) as sb:
        links = get_links_bizbuysell(sb, max_listings)

        for i, link in enumerate(links, 1):
            print(f"[BizBuySell {i}/{len(links)}]")
            sb.uc_open_with_reconnect(link, reconnect_time=3)
            sb.wait_for_element("body", timeout=10)
            sb.sleep(2)

            body = sb.get_text("body")

            title = (
                sb.get_text("h1").strip()
                if sb.is_element_present("h1")
                else "BizBuySell Listing"
            )

            asking = find_value("asking", body)
            revenue = find_value("revenue", body)
            cashflow = find_value("cash flow", body)

            results.append({
                "Business Name": title,
                "Industry": "Not Specified",
                "Location": "Not Specified",
                "Asking Price": normalize_money(asking),
                "Revenue": normalize_money(revenue),
                "EBITDA": normalize_money(cashflow),
                "Years in Operation": "Not Disclosed",
                "Broker or Seller Contact": "Not Available",
                "Listing URL": link,
                "Source": "BizBuySell",
            })

            sb.sleep(2)

            if len(results) >= max_listings:
                break

    print(f"BizBuySell Complete: {len(results)} listings scraped")
    return results


# ================== SAVE OUTPUT ================= #

def save_output(listings):
    output_dir = os.path.join("agent_1", "output")
    os.makedirs(output_dir, exist_ok=True)

    path = os.path.join(output_dir, "bizbuysell_listings.csv")
    df = pd.DataFrame(listings)
    df.to_csv(path, index=False)

    print(f"\n📁 bizbuysell_listings.csv saved ({len(df)} rows)")


# ================== MAIN RUNNER ================= #

if __name__ == "__main__":
    listings = scrape_bizbuysell(max_listings=5)
    save_output(listings)
