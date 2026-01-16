from typing import TypedDict, List, Dict, Optional, Annotated, Any
from operator import add


class CatalogRecord(TypedDict):
    """Single catalog record"""
    record_id: str
    record_type: str  # "listing", "broker", "email"
    business_name: Optional[str]
    broker_name: Optional[str]
    industry_tag: str
    size_tag: str
    geography_tag: str
    deal_status: str
    raw_data: Dict


class AgentState(TypedDict, total=False):
    """State for Data Catalog Agent"""
    # Input data - DataFrames from load_data_node
    listings_df: Any  # pd.DataFrame
    brokers_df: Any   # pd.DataFrame
    emails_df: Any    # pd.DataFrame
    
    # Legacy support (optional)
    listings_data: List[Dict]
    brokers_data: List[Dict]
    emails_data: List[Dict]
    
    # Processed
    catalog_records: Annotated[List[CatalogRecord], add]
    
    # Tags summary
    tag_summary: Dict[str, int]
    
    # Metadata
    total_records: int
    errors: Annotated[List[str], add]
    current_stage: str
    output_paths: Dict[str, str]