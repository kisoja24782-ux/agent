from langchain.agents import create_agent

from ex_1008.supervisor_agent_triple.handoff_tools import create_handoff_tool
from ex_1008.supervisor_agent_triple.web_agent import create_web_agent
from ex_1008.supervisor_agent_triple.db_agent import create_db_search_agent
from ex_1008.supervisor_agent_triple.faq_agent import create_faq_agent
from ex_1008.supervisor_agent_triple.settings import get_model, get_system_prompt

agents = {
    "web_search": create_web_agent,
    "db_search": create_db_search_agent,
    "faq": create_faq_agent
}

handoff_tools = [
    create_handoff_tool(
        agent_name= "web_search",
        description= "웹에서 최신 정보를 검색해야 할 때 사용합니다."
    ),
    create_handoff_tool(
        agent_name= "db_search",
        description= "내무 데이터베이스에서 문서 정보를 검색해야 할 때 사용합니다."
    ),
    create_handoff_tool(
        agent_name= "faq",
        description= "자주 묻는 질문에 대해 답변해야 할 때 사용합니다."
    )
]

model = get_model(model_name= "gpt-4o")

supervisor = create_agent(
    model= model,
    tools= handoff_tools,
    system_prompt= get_system_prompt()
)