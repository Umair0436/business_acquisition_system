from langgraph.graph import StateGraph, END
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.state import AgentState
from agent.nodes.load_data import load_data_node
from agent.nodes.tag_data import tag_data_node
from agent.nodes.organize_data import organize_data_node
from agent.nodes.export_data import export_data_node


def create_catalog_graph():
    """Create LangGraph workflow for Data Catalog Agent"""
    
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("load_data", load_data_node)
    workflow.add_node("tag_data", tag_data_node)
    workflow.add_node("organize_data", organize_data_node)
    workflow.add_node("export_data", export_data_node)
    
    # Define flow
    workflow.set_entry_point("load_data")
    workflow.add_edge("load_data", "tag_data")
    workflow.add_edge("tag_data", "organize_data")
    workflow.add_edge("organize_data", "export_data")
    workflow.add_edge("export_data", END)
    
    # Compile
    app = workflow.compile()
    
    return app