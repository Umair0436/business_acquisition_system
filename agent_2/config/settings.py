import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent.parent
INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"

# Ensure directories exist
INPUT_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# File paths
INPUT_CSV = INPUT_DIR / "listings.csv"
OUTPUT_CSV = OUTPUT_DIR / "Master_Broker_Database.csv"

# Scraping settings
SCRAPING_CONFIG = {
    "headless": False,  # Set True for production
    "page_load_timeout": 30,
    "implicit_wait": 10,
    "retry_attempts": 3,
    "delay_between_requests": (3, 7),  # Random delay range
}

# Keywords to identify form-based contacts
FORM_KEYWORDS = ["form", "contact form", "inquiry", "request info", "name: form"]

# Regex patterns
EMAIL_REGEX = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
PHONE_REGEX = r'(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'

# LinkedIn search template
LINKEDIN_SEARCH_TEMPLATE = "https://www.linkedin.com/search/results/people/?keywords={name}%20{firm}&origin=GLOBAL_SEARCH_HEADER"