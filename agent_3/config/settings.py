from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"

INPUT_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

BROKER_DATABASE_CSV = INPUT_DIR / "Master_Broker_Database.csv"
EMAIL_DRAFTS_CSV = OUTPUT_DIR / "email_drafts.csv"

# Email generation settings
EMAIL_CONFIG = {
    "max_emails_per_run": 50,  # Safety limit
    "skip_without_email": True,  # Skip brokers without email addresses
}

# Available tones
AVAILABLE_TONES = {
    "professional": "Professional / Institutional",
    "relationship": "Relationship-based / Warm",
    "direct": "Short & Direct"
}

# User info (customize this)
USER_INFO = {
    "name": "John Smith",  # ← Change this
    "company": "Acquisition Capital Partners",  # ← Change this
    "title": "Senior Acquisitions Manager",  # ← Change this
    "phone": "+1-555-123-4567",  # ← Change this
    "email": "john.smith@acqcapital.com"  # ← Change this
}