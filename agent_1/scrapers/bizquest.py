from seleniumbase import SB
import re
import time


# ---------------- helpers ----------------

def normalize_money(text):
    if not text:
        return 0
    text = str(text).lower().replace("$", "").replace(",", "").strip()
    if any(w in text for w in ["disclosed", "n/a", "none", "call"]):
        return 0

    mult = 1
    if "m" in text:
        mult = 1_000_000
        text = text.replace("m", "")
    elif "k" in text:
        mult = 1_000
        text = text.replace("k", "")

    m = re.search(r"[\d.]+", text)
    return int(float(m.group()) * mult) if m else 0


def find_value(keyword, text):
    patterns = [
        rf"{keyword}[:\s]*\$?([\d,.KkMm]+)",
        rf"{keyword}.*?\$?([\d,.KkMm]+)",
    ]
    for p in patterns:
        m = re.search(p, text, re.I)
        if m:
            return m.group(1)
    return None


# ---------------- core scraper ----------------

def scrape_single_listing(sb, url):
    try:
        sb.uc_open_with_reconnect(url, reconnect_time=1)
        sb.sleep(1)  # allow JS to load

        body = sb.get_text("body")

        # safer title extraction
        title = None
        possible_titles = [
            "h1",
            "h2",
            "meta[property='og:title']",
            "title",
        ]

        for selector in possible_titles:
            try:
                title = sb.get_text(selector)
                if title and len(title) > 5:
                    break
            except:
                continue

        if not title:
            title = "BizQuest Business Listing"

        asking = find_value("asking price", body)
        revenue = find_value("revenue", body)
        cashflow = find_value("cash flow", body)

        return {
            "Business Name": title.strip(),
            "Industry": "Not Specified",
            "Location": "Not Specified",
            "Asking Price": normalize_money(asking),
            "Revenue": normalize_money(revenue),
            "EBITDA": normalize_money(cashflow),
            "Years in Operation": "Not Disclosed",
            "Broker or Seller Contact": "Not Available",
            "Listing URL": url,
            "Source": "BizQuest",
        }

    except Exception as e:
        print(f"   ❌ Failed listing: {e}")
        return None



def get_links(sb, max_links):
    url = "https://www.bizquest.com/businesses-for-sale/"
    sb.uc_open_with_reconnect(url, reconnect_time=1)
    sb.wait_for_element_present("a[href*='/business-for-sale/']", timeout=20)
    sb.sleep(1)

    links = []
    for a in sb.find_elements("a[href*='/business-for-sale/']"):
        try:
            href = a.get_attribute("href")
            if href and "bizquest.com/business-for-sale/" in href:
                if href not in links:
                    links.append(href)
                if len(links) >= max_links:
                    break
        except:
            pass

    return links


# ---------------- PIPELINE ENTRY POINT ----------------

def scrape_bizquest(max_listings=10, max_pages=3):
    """
    REQUIRED BY PIPELINE
    Returns list[dict]
    """

    print(f"Target: {max_listings} listings from {max_pages} pages")
    results = []

    with SB(uc=True, headless=False) as sb:
        links = get_links(sb, max_listings)

        for i, link in enumerate(links, 1):
            print(f"[BizQuest {i}/{len(links)}]")
            data = scrape_single_listing(sb, link)
            if data:
                results.append(data)
                print(f"   Found: {data['Business Name'][:40]}")
            time.sleep(1)

    print(f"BizQuest Complete: {len(results)} listings scraped")
    return results
