from langgraph.graph import StateGraph, START, END
from langgraph.graph import MessagesState

from planning_agent import planning_node
from supervisor_agent import supervisor_node
from canvas_agent import canvas_node
from research_agent import research_node
from settings import State

graph_builder = StateGraph(State, input_schema= MessagesState, output_schema= State)

graph_builder.add_node("planning", planning_node, destinations= ["supervisor", END])
graph_builder.add_node("supervisor", supervisor_node, destinations= ["canvas", "research", "planning"])
graph_builder.add_node("canvas", canvas_node, destinations= ["supervisor"])
graph_builder.add_node("research", research_node, destinations= ["supervisor"])

graph_builder.add_edge(START, "planning")

graph = graph_builder.compile()