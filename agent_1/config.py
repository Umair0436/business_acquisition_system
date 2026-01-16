# agent_1/config.py
"""
Configuration for Business Listing Scraper
Control number of listings per website
"""

# Scraping Configuration
SCRAPING_CONFIG = {
    "bizbuysell": {
        "enabled": True,
        "max_listings": 1,  # Change yeh number
        "max_pages": 3,      # Zyada pages = zyada listings
    },
    "bizquest": {
        "enabled": True,
        "max_listings": 1,  # Change yeh number
        "max_pages": 3,
    },
    "loopnet": {
        "enabled": True,
        "max_listings": 1,  # Change yeh number
        "max_pages": 3,
    }
}

# General Settings
GENERAL_CONFIG = {
    "headless": False,           # False = browser dikhegi
    "delay_between_pages": 3,    # Seconds
    "delay_between_listings": 2, # Seconds
    "timeout": 30,               # Page load timeout
}

# Output Settings
OUTPUT_CONFIG = {
    "output_file": "output/listings.csv",
    "save_intermediate": True,   # Save after each website
}