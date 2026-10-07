from langgraph.graph import StateGraph, MessagesState, START
from ex_1007.network_agent.research_agent import research_node
from ex_1007.network_agent.chart_agent import html_node

graph_builder = StateGraph(MessagesState)
graph_builder.add_node("researcher", research_node)
graph_builder.add_node("html_generator", html_node)

graph_builder.add_edge(START, "researcher")
graph = graph_builder.compile()