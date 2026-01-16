from langgraph.graph import StateGraph, END
import sys
from pathlib import Path

# Fix imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.state import AgentState
from agent.nodes.filter_node import filter_listings_node
from agent.nodes.extraction_node import deep_extraction_node
from agent.nodes.duplication_node import deduplicate_brokers_node
from agent.nodes.enrichment_node import enrich_brokers_node
from agent.nodes.export_node import export_brokers_node


def create_broker_intelligence_graph():
    """Create LangGraph workflow"""
    
    workflow = StateGraph(AgentState)
    
    workflow.add_node("filter", filter_listings_node)
    workflow.add_node("extract", deep_extraction_node)
    workflow.add_node("deduplicate", deduplicate_brokers_node)
    workflow.add_node("enrich", enrich_brokers_node)
    workflow.add_node("export", export_brokers_node)
    
    workflow.set_entry_point("filter")
    workflow.add_edge("filter", "extract")
    workflow.add_edge("extract", "deduplicate")
    workflow.add_edge("deduplicate", "enrich")
    workflow.add_edge("enrich", "export")
    workflow.add_edge("export", END)
    
    app = workflow.compile()
    
    return app