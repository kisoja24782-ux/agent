from typing import Annotated
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch

from dotenv import load_dotenv

load_dotenv()

### 도구 정의 ###

tool = TavilySearch(max_results=3)
tools = [tool]

llm = ChatOpenAI(model="gpt-4o")
llm_with_tools = llm.bind_tools(tools)


### 그래프 상태 정의 ###

class State(TypedDict):
    messages: Annotated[list, add_messages]

graph_builder = StateGraph(State)


### 그래프 노드 추가 ###

#### 챗봇 노드 ####

def chatbot(state: State):
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

graph_builder.add_node("chatbot", chatbot)

import json
from langchain_core.messages import ToolMessage

class BasicToolNode:
    """
        마지막 AIMessage에서 요청된 도구를 실행하는 노드
    """

    def __init__(self, tools: list) -> None:
        self.tools_by_name = {tool.name: tool for tool in tools}

    def __call__(self, inputs: dict):
        if messages := inputs.get("messages", []):
            message = messages[-1]
        else:
            raise ValueError("Error: 입력에 메시지가 없습니다.")

        outputs = []
        for tool_call in message.tool_calls:
            tool_result = self.tools_by_name[tool_call["name"]].invoke(tool_call["args"])
            outputs.append(ToolMessage(
                content= json.dumps(tool_result, ensure_ascii= False),
                name= tool_call["name"],
                tool_call_id = tool_call["id"]
                )
            )

        return {"messages" : outputs}


tool_node = BasicToolNode(tools = [tool])
graph_builder.add_node("tools",tool_node)