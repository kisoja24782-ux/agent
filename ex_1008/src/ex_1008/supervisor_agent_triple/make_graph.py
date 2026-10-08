from langgraph.graph import StateGraph, MessagesState, END
from ex_1008.supervisor_agent_triple.supervisor_agent import supervisor, agents
from ex_1008.supervisor_agent_triple.settings import AgentState

graph_builder = StateGraph(MessagesState) # MessagesState -> AgentState

agent_names = list(agents.keys())
graph_builder.add_node(
    "supervisor",
    supervisor,
    destinations=tuple(agent_names) + (END,)
)

graph_builder.add_node("web_search", agents["web_search"])
graph_builder.add_node("db_search", agents["db_search"])
graph_builder.add_node("faq", agents["faq"])

graph_builder.set_entry_point("supervisor")

for agent_name in agents.keys():
    graph_builder.add_edge(agent_name, "supervisor")

graph = graph_builder.compile()