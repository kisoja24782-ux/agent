from langgraph.graph import StateGraph, START, END
from langgraph.graph import MessagesState

from ex_1009.supervisor_planning_agent.planning_agent import planning_node
from ex_1009.supervisor_planning_agent.supervisor_agent import supervisor_node
from ex_1009.supervisor_planning_agent.canvas_agent import canvas_node
from ex_1009.supervisor_planning_agent.research_agent import research_node
from ex_1009.supervisor_planning_agent.settings import State

graph_builder = StateGraph(State, input_schema= MessagesState, output_schema= State)

graph_builder.add_node("planning", planning_node, destinations= ["supervisor", END])
graph_builder.add_node("supervisor", supervisor_node, destinations= ["canvas", "research", "planning"])
graph_builder.add_node("canvas", canvas_node, destinations= ["supervisor"])
graph_builder.add_node("research", research_node, destinations= ["supervisor"])

graph_builder.add_edge(START, "planning")

graph = graph_builder.compile()