import re
from typing import Optional


def validate_email(email: Optional[str]) -> bool:
    """Validate email format"""
    if not email:
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone(phone: Optional[str]) -> bool:
    """Validate phone format"""
    if not phone:
        return False
    digits = re.sub(r'\D', '', phone)
    return len(digits) >= 10


def normalize_name(name: Optional[str]) -> Optional[str]:
    """Normalize broker name for comparison"""
    if not name:
        return None
    
    name = ' '.join(name.split())
    name = name.title()
    
    # Remove common titles
    name = re.sub(r'\b(Mr|Mrs|Ms|Dr|Jr|Sr)\.?\b', '', name, flags=re.IGNORECASE)
    
    return name.strip()


def normalize_firm(firm: Optional[str]) -> Optional[str]:
    """Normalize firm name for comparison"""
    if not firm:
        return None
    
    # Remove common suffixes
    firm = re.sub(r',?\s*(LLC|Inc|Corp|Ltd|LLP|LP)\.?$', '', firm, flags=re.IGNORECASE)
    firm = ' '.join(firm.split())
    
    return firm.strip()