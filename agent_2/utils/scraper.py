from seleniumbase import SB
from typing import Optional, Dict
import re
import time
import random
from config.settings import SCRAPING_CONFIG, EMAIL_REGEX


class BrokerScraper:
    """SeleniumBase UC Mode scraper for broker extraction"""

    def __init__(self):
        self.config = SCRAPING_CONFIG

    def extract_broker_data(self, url: str) -> Dict[str, Optional[str]]:
        broker_data = {
            "broker_name": None,
            "brokerage_firm": None,
            "email": None,
            "phone": None,
            "industry_focus": None,
            "location": None,          # used by Agent-2
            "source_url": url,
        }

        with SB(uc=True, headless=self.config["headless"]) as sb:
            try:
                sb.open(url)
                sb.sleep(random.uniform(3, 5))

                self._try_click_contact_button(sb)
                sb.sleep(2)

                page_source = sb.get_page_source()

                broker_data["broker_name"] = self._extract_broker_name(sb, page_source)
                broker_data["brokerage_firm"] = self._extract_brokerage_firm(sb, page_source)
                broker_data["email"] = self._extract_email(sb, page_source)
                broker_data["phone"] = self._extract_phone(page_source)
                broker_data["industry_focus"] = self._extract_industry(sb, page_source)
                broker_data["location"] = self._extract_geography(sb, page_source)

                return broker_data

            except Exception as e:
                print(f"  ❌ Error: {str(e)[:60]}")
                return broker_data

    # ----------------------- HELPERS -----------------------

    def _try_click_contact_button(self, sb):
        contact_selectors = [
            "a:contains('Contact Seller')",
            "a:contains('Contact Broker')",
            "button:contains('Contact')",
            "a:contains('Show Phone')",
            "button:contains('Show Phone')",
            "[class*='contact']",
            "[class*='phone']",
        ]

        for selector in contact_selectors:
            try:
                if sb.is_element_visible(selector, timeout=1):
                    sb.click(selector)
                    print("  ✓ Clicked contact button")
                    return True
            except Exception:
                continue
        return False

    def _extract_broker_name(self, sb, page_source: str) -> Optional[str]:
        selectors = [
            "[class*='broker-name']",
            "[class*='agent-name']",
            "[class*='contact-name']",
        ]

        for selector in selectors:
            try:
                for el in sb.find_elements(selector):
                    text = el.text.strip()
                    if text and " " in text and 5 < len(text) < 50:
                        return self._clean_name(text)
            except Exception:
                continue

        patterns = [
            r'Broker[:\s]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
            r'Agent[:\s]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
            r'Listed by[:\s]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
        ]

        for p in patterns:
            m = re.search(p, page_source)
            if m:
                return self._clean_name(m.group(1))

        return None

    def _extract_brokerage_firm(self, sb, page_source: str) -> Optional[str]:
        selectors = [
            "[class*='brokerage']",
            "[class*='company']",
            "[class*='firm']",
        ]

        for selector in selectors:
            try:
                for el in sb.find_elements(selector):
                    text = el.text.strip()
                    if text and 5 < len(text) < 80:
                        return self._clean_firm(text)
            except Exception:
                continue

        return None

    def _extract_email(self, sb, page_source: str) -> Optional[str]:
        """Improved email extraction with mailto links & filtering"""
        emails = []

        # 1️⃣ Plain text emails
        emails += re.findall(EMAIL_REGEX, page_source)

        # 2️⃣ Mailto: links
        try:
            mailto_links = sb.find_elements("a[href^='mailto:']")
            for el in mailto_links:
                href = el.get_attribute("href")
                if href:
                    email = href.replace("mailto:", "").split("?")[0]
                    emails.append(email)
        except Exception:
            pass

        # 3️⃣ Filter invalid / test emails
        emails = [e for e in emails if not any(x in e.lower() for x in ["noreply", "example.com", "test@"])]

        return emails[0] if emails else None

    def _extract_phone(self, page_source: str) -> Optional[str]:
        patterns = [
            r'\((\d{3})\)\s*(\d{3})[-\s]?(\d{4})',
            r'(\d{3})[-.\s](\d{3})[-.\s](\d{4})',
        ]

        for p in patterns:
            for m in re.findall(p, page_source):
                if all(part.isdigit() for part in m):
                    return f"+1-{m[0]}-{m[1]}-{m[2]}"
        return None

    def _extract_industry(self, sb, page_source: str) -> Optional[str]:
        selectors = ["[class*='category']", "[class*='industry']"]
        for selector in selectors:
            try:
                el = sb.find_element(selector)
                text = el.text.strip()
                if text and len(text) < 50:
                    return text
            except Exception:
                continue
        return None

    def _extract_geography(self, sb, page_source: str) -> Optional[str]:
        """Robust geography: selector fallback + regex"""
        selectors = [
            "[class*='location']",
            "[class*='address']",
            "[class*='city']",
        ]

        for selector in selectors:
            try:
                el = sb.find_element(selector)
                text = el.text.strip()
                if text and len(text) < 100:
                    return text
            except Exception:
                continue

        # Regex fallback: City, State
        match = re.search(r"[A-Z][a-z]+,\s?[A-Z]{2}", page_source)
        if match:
            return match.group(0)

        return None

    # ----------------------- CLEANERS -----------------------

    def _clean_name(self, name: str) -> str:
        name = re.sub(r'^(Broker|Agent|Contact|By)[:,\s]*', '', name, flags=re.I)
        return re.sub(r'\s+', ' ', name).strip()

    def _clean_firm(self, firm: str) -> str:
        firm = re.sub(r'^(Brokerage|Firm|Company)[:,\s]*', '', firm, flags=re.I)
        return re.sub(r'\s+', ' ', firm).strip()


def random_delay():
    delay = random.uniform(*SCRAPING_CONFIG["delay_between_requests"])
    time.sleep(delay)
