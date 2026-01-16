from langgraph.graph import StateGraph, END
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.state import AgentState
from agent.nodes.load_brokers import load_brokers_node
from agent.nodes.generate_emails import generate_emails_node
from agent.nodes.export_drafts import export_drafts_node


def create_email_outreach_graph():
    """Create LangGraph workflow for Email Outreach Agent"""
    
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("load_brokers", load_brokers_node)
    workflow.add_node("generate_emails", generate_emails_node)
    workflow.add_node("export_drafts", export_drafts_node)
    
    # Define flow
    workflow.set_entry_point("load_brokers")
    workflow.add_edge("load_brokers", "generate_emails")
    workflow.add_edge("generate_emails", "export_drafts")
    workflow.add_edge("export_drafts", END)
    
    # Compile
    app = workflow.compile()
    
    return app