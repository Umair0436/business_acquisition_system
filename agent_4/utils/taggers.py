import re
from typing import Optional
from config.settings import INDUSTRY_TAGS, SIZE_TAGS


def tag_industry(business_name: str, industry: str) -> str:
    """Tag industry based on business name and industry field"""
    
    text = f"{business_name} {industry}".lower()
    
    for tag, keywords in INDUSTRY_TAGS.items():
        if any(keyword in text for keyword in keywords):
            return tag
    
    return "other"


def tag_size(asking_price: str, revenue: str) -> str:
    """Tag size based on price and revenue"""
    
    # Extract numbers
    price = extract_number(asking_price)
    rev = extract_number(revenue)
    
    # Use whichever is available
    amount = price or rev or 0
    
    for tag, (min_val, max_val) in SIZE_TAGS.items():
        if min_val <= amount < max_val:
            return tag
    
    return "unknown"


def tag_geography(location: str) -> str:
    """Extract and tag geography"""
    
    if not location or location == "Not Specified":
        return "unknown"
    
    # Extract state if present
    state_match = re.search(r'\b([A-Z]{2})\b', location)
    if state_match:
        return state_match.group(1)
    
    # Extract city
    parts = location.split(',')
    if parts:
        return parts[0].strip()
    
    return location[:50]


def tag_deal_status(record_type: str) -> str:
    """Initial deal status based on record type"""
    
    if record_type == "listing":
        return "new_lead"
    elif record_type == "broker":
        return "contacted"
    elif record_type == "email":
        return "contacted"
    
    return "new_lead"


def extract_number(value: str) -> Optional[float]:
    """Extract numeric value from string"""
    
    if not value or value in ["Not Specified", "N/A", "nan"]:
        return None
    
    # Remove $ and commas
    clean = re.sub(r'[$,]', '', str(value))
    
    try:
        return float(clean)
    except:
        return None