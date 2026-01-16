from langgraph.graph import StateGraph
from listing_agents.agent import run_listing_agent
from graph.state import GraphState

graph = StateGraph(GraphState)

graph.add_node("listing_agent", run_listing_agent)
graph.set_entry_point("listing_agent")

app = graph.compile()
