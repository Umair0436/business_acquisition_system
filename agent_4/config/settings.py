from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"

INPUT_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# Input files
LISTINGS_CSV = INPUT_DIR / "listings.csv"
BROKERS_CSV = INPUT_DIR / "Master_Broker_Database.csv"
EMAILS_CSV = INPUT_DIR / "email_drafts.csv"

# Output files
MASTER_EXCEL = OUTPUT_DIR / "Master_Database.xlsx"
MASTER_CSV = OUTPUT_DIR / "Master_Database.csv"
NOTION_JSON = OUTPUT_DIR / "notion_export.json"
AIRTABLE_JSON = OUTPUT_DIR / "airtable_export.json"

# Tagging rules
INDUSTRY_TAGS = {
    "technology": ["tech", "software", "saas", "it", "digital"],
    "food_beverage": ["restaurant", "cafe", "bar", "food", "beverage", "bakery"],
    "healthcare": ["medical", "dental", "healthcare", "clinic", "spa"],
    "retail": ["store", "shop", "retail", "boutique"],
    "real_estate": ["property", "real estate", "commercial"],
    "automotive": ["auto", "car", "automotive", "repair"],
    "services": ["service", "consulting", "cleaning"],
    "manufacturing": ["manufacturing", "production", "factory"],
    "other": []
}

SIZE_TAGS = {
    "micro": (0, 250000),           # < $250k
    "small": (250000, 1000000),     # $250k - $1M
    "medium": (1000000, 5000000),   # $1M - $5M
    "large": (5000000, float('inf')) # > $5M
}

DEAL_STATUS_OPTIONS = [
    "new_lead",
    "contacted",
    "in_discussion",
    "on_hold",
    "closed",
    "rejected"
]