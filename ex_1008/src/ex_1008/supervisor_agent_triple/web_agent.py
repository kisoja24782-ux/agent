from langchain.agents import create_agent
from langchain_tavily import TavilySearch
from langgraph.graph import END
from langgraph.types import Command
from langchain.messages import HumanMessage
from ex_1008.supervisor_agent_triple.handoff_tools import create_handoff_messages
from ex_1008.supervisor_agent_triple.settings import AgentState, get_model

model = get_model(model_name= "gpt-4o")
taivly_search = TavilySearch(max_results = 3)

web_agent = create_agent(model= model, tools=[taivly_search])

def create_web_agent(state: AgentState) -> Command:
    query = state.get("query", "")
    agent_state = {"messages": [HumanMessage(content=query)]}

    result = web_agent.invoke(agent_state)

    ai_message, tool_message = create_handoff_messages("web_search")

    result["messages"].extend([ai_message, tool_message])

    return Command(update={"messages": result["messages"]}, goto= END)