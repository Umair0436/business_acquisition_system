from typing import TypedDict, List, Dict, Optional, Annotated
from operator import add


class BrokerRecord(TypedDict):
    """Individual broker record structure"""
    broker_name: Optional[str]
    brokerage_firm: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    industry_focus: Optional[str]
    geography: Optional[str]
    linkedin_search_url: Optional[str]
    source_listing_url: str
    extraction_timestamp: str


class AgentState(TypedDict):
    """Main state for Broker Intelligence Agent"""
    # Input data
    input_listings: List[Dict[str, str]]
    listings_to_process: List[Dict[str, str]]
    
    # Processing tracking
    current_index: int
    total_listings: int
    
    # Broker database (cumulative)
    broker_database: Annotated[List[BrokerRecord], add]
    
    # Metadata
    processed_count: int
    skipped_count: int
    errors: Annotated[List[str], add]
    current_stage: str
    
    # Configuration
    output_path: str