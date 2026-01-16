from typing import TypedDict, List, Dict, Optional, Annotated
from operator import add


class EmailDraft(TypedDict):
    """Single email draft"""
    broker_name: str
    broker_firm: str
    broker_email: Optional[str]
    email_subject: str
    email_body: str
    tone: str
    generation_timestamp: str


class AgentState(TypedDict):
    """State for Email Outreach Agent"""
    # Input
    broker_database: List[Dict[str, str]]
    selected_tone: str  # "professional", "relationship", "direct"
    
    # Processing
    email_drafts: Annotated[List[EmailDraft], add]
    
    # Metadata
    total_brokers: int
    drafts_generated: int
    errors: Annotated[List[str], add]
    current_stage: str
    output_path: str