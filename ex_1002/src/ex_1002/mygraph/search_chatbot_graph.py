"""
[전체 흐름 요약]
"검색 도구를 쓸 수 있는 챗봇"을 LangGraph로 만든 예제.

    START
      │
      ▼
   chatbot  ──(도구 호출 있음)──▶  tools
      │  ▲                          │
      │  └──────────────────────────┘   (도구 결과를 들고 다시 chatbot으로)
      │
   (도구 호출 없음)
      ▼
     END

1) 사용자 질문이 State["messages"]에 들어간 채로 그래프가 시작됨
2) chatbot 노드: LLM(gpt-4o)이 질문을 보고
   - 바로 답할 수 있으면 → 일반 답변(AIMessage) 생성 → END
   - 검색이 필요하면 → "TavilySearch를 이런 인자로 호출해줘"라는 tool_calls가 담긴 AIMessage 생성
3) route_tools: 마지막 메시지에 tool_calls가 있으면 "tools"로, 없으면 END로 보냄
4) tools 노드: 실제로 Tavily 검색을 실행하고 결과를 ToolMessage로 State에 추가
5) 다시 chatbot으로 돌아가 LLM이 검색 결과를 읽고 최종 답변 생성 → (보통) END
"""

from typing import Annotated
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch

from dotenv import load_dotenv

# .env 파일에서 OPENAI_API_KEY, TAVILY_API_KEY 같은 환경변수를 읽어옴
load_dotenv()

### 도구와 AI준비###

# Tavily 웹 검색 도구. 한 번 검색할 때 최대 3개의 결과를 돌려줌
tool = TavilySearch(max_results=3)
tools = [tool]

llm = ChatOpenAI(model="gpt-4o")
# bind_tools : 너는 이런 검색도구를 쓸 수 있어
# → 도구의 이름/설명/인자 스키마가 LLM 요청에 함께 전달됨.
#   LLM은 도구를 "직접 실행"하지 않고, 필요하면 응답에 tool_calls(어떤 도구를 어떤 인자로)만 적어 보냄.
#   실제 실행은 아래 BasicToolNode가 담당.
llm_with_tools = llm.bind_tools(tools)


### 그래프 상태 정의 ###

# 그래프의 모든 노드가 공유하는 상태(State)
# messages: 대화 기록 리스트
# Annotated[..., add_messages] : 노드가 {"messages": [...]}를 반환하면
#   기존 리스트를 "덮어쓰지" 않고 뒤에 "이어 붙이라"는 규칙(reducer).
#   또 "문자열"을 넣으면 자동으로 HumanMessage로 변환해줌 (아래 invoke에서 문자열을 넣는 이유)
class State(TypedDict):
    messages: Annotated[list, add_messages]

# State 구조를 사용하는 그래프 설계도(builder) 생성. 노드/엣지를 붙인 뒤 compile()해야 실행 가능
graph_builder = StateGraph(State)


### 그래프 노드 추가 ###

#### 챗봇 노드 ####

# 지금까지의 대화 전체를 LLM에 넘겨 다음 응답(AIMessage)을 받음.
# 응답은 일반 답변일 수도, tool_calls가 들어 있는 "도구 호출 요청"일 수도 있음.
# 반환값 {"messages": [response]}는 add_messages 덕분에 기존 대화 뒤에 추가됨
def chatbot(state: State):
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

# "chatbot"이라는 이름으로 노드 등록
graph_builder.add_node("chatbot", chatbot)


 ## 도구 실행 노드

import json
from langchain_core.messages import ToolMessage

# LangGraph에 내장된 ToolNode(langgraph.prebuilt)를 직접 구현해본 클래스.
# __call__이 있어서 인스턴스를 함수처럼 노드로 등록할 수 있음
class BasicToolNode:
    """
        마지막 AIMessage에서 요청된 도구를 실행하는 노드
    """

    def __init__(self, tools: list) -> None:
        # 도구 이름 → 도구 객체 딕셔너리 (예: {"tavily_search": TavilySearch객체})
        # LLM이 tool_calls에 적어준 "이름"으로 실제 도구를 찾기 위함
        self.tools_by_name = {tool.name: tool for tool in tools}

    # __call__ 객체를 함수처럼 부를 수 있게됨
    def __call__(self, inputs: dict):
        # State에서 가장 마지막 메시지(= chatbot이 방금 만든 AIMessage)를 꺼냄
        # :=는 값을 변수에 넣으면서 동시에 조건 검사를 하는 문법이에요. "messages를 꺼내서 변수에 담고, 비어 있지 않으면"이라는 뜻
        if messages := inputs.get("messages", []):
            message = messages[-1]
        else:
            raise ValueError("Error: 입력에 메시지가 없습니다.")

        outputs = []
        # LLM이 요청한 도구 호출을 하나씩 실행 (한 번에 여러 개를 요청할 수도 있음)
        # tool_call 예: {"name": "tavily_search", "args": {"query": "LangGraph"}, "id": "call_abc123"}
        for tool_call in message.tool_calls:
            # 이름으로 도구를 찾아 인자를 넣고 실제 실행 (여기서 Tavily 검색 API 호출)
            tool_result = self.tools_by_name[tool_call["name"]].invoke(tool_call["args"])
            # 실행 결과를 ToolMessage로 포장.
            # - content: 결과를 JSON 문자열로 (ensure_ascii=False → 한글이 \uXXXX로 깨지지 않게)
            # - tool_call_id: 어떤 요청에 대한 응답인지 LLM이 짝을 맞출 수 있도록 반드시 필요
            outputs.append(ToolMessage(
                content= json.dumps(tool_result, ensure_ascii= False),
                name= tool_call["name"],
                tool_call_id = tool_call["id"]
                )
            )

        # 도구 결과 메시지들을 State의 messages 뒤에 추가
        return {"messages" : outputs}


tool_node = BasicToolNode(tools = [tool])
# "tools"라는 이름으로 도구 실행 노드 등록
graph_builder.add_node("tools",tool_node)

# 조건부 엣지 추가

# chatbot 노드가 끝난 뒤 "다음에 어디로 갈지" 결정하는 라우터 함수.
# 반환한 값("tools" 또는 END)이 아래 add_conditional_edges의 매핑 키로 쓰임
def route_tools(state: State):
    """
    마지막 메시지에 도구 호출이 있는 경우, ToolNode로 라우팅하고 그렇지 않으면 END로 라우팅
    """
    # state가 메시지 리스트 그 자체로 들어오는 경우와 dict(State)로 들어오는 경우 둘 다 처리
    if isinstance(state, list):
        ai_message = state[-1]
    elif messages := state.get("messages", []):
        ai_message = messages[-1]
    else:
        raise ValueError(f"ERROR : 입력에 메시지가 없습니다. 상태 : {state}")

    # LLM이 도구 호출을 요청했으면 → "tools" 노드로
    if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
        return "tools"
    # 도구 호출이 없으면 = 최종 답변이 나온 것 → 그래프 종료
    return END


# chatbot 실행 후 route_tools의 반환값에 따라 분기
#   "tools" 반환 → "tools" 노드로 이동
#   END 반환    → 그래프 종료
graph_builder.add_conditional_edges(
    "chatbot",
    route_tools,
    {"tools": "tools", END: END}
)

### 나머지 엣지 추가 및 그래프 컴파일 ###

# 도구 실행이 끝나면 항상 chatbot으로 돌아가 LLM이 결과를 보고 답하게 함 (이 때문에 루프가 생김)
graph_builder.add_edge("tools", "chatbot")
# 그래프 시작점 → chatbot
graph_builder.add_edge(START, "chatbot")
# 설계도를 실행 가능한 그래프로 변환 (invoke / stream 등을 쓸 수 있게 됨)
graph = graph_builder.compile()


# ------------------------------------------------------------------
# 아래는 같은 그래프를 여러 방식으로 실행해보는 함수들
# 입력 {"messages": ["질문"]} 의 문자열은 add_messages가 HumanMessage로 바꿔줌
# ------------------------------------------------------------------

# [동기 실행] 그래프가 END에 도달할 때까지 전부 돌린 뒤 "최종 State"를 한 번에 받음.
# 출력 순서 예: HumanMessage → AIMessage(tool_calls) → ToolMessage(검색 결과) → AIMessage(최종 답변)
def invoke():
    response = graph.invoke(
        {
            "messages" : ["Langgraph가 무엇인가요?"]
        }
    )

    for msg in response["messages"]:
        msg.pretty_print()

# [비동기 실행] invoke와 결과는 같고, async/await로 실행 (asyncio.run(ainvoke())로 호출)
async def ainvoke():
    response = await graph.ainvoke(
        {
            "messages" : ["Langgraph가 무엇인가요?"]
        }
    )

    for msg in response["messages"]:
        msg.pretty_print()


# [스트리밍 - 기본 모드 "updates"] 노드가 하나 끝날 때마다 결과를 바로 받음.
# chunk 형태: {"노드이름": 그 노드가 반환한 값}
#   예) {"chatbot": {"messages": [AIMessage]}} → {"tools": {"messages": [ToolMessage]}} → {"chatbot": ...}
# 즉 "그 노드가 새로 추가한 것"만 보여줌
def stream():
    response = graph.stream(
        {
            "messages": ["Langgraph가 무엇인가요?"]
        }
    )

    for chunk in response:
        for node, state in chunk.items():
            print("---", node, "---")
            print(state)
            print("=" * 60)


# [스트리밍 - "values" 모드] 매 단계마다 "그 시점의 State 전체"를 받음.
# chunk 형태: {"messages": [지금까지 쌓인 모든 메시지]}
# 단계가 진행될수록 메시지 리스트가 점점 길어지는 것을 확인할 수 있음
def stream_values():
    response = graph.stream(
        {
            "messages": ["Langgraph가 무엇인가요?"]
        },
        stream_mode= "values"
    )

    for chunk in response:
        for state_key, state_value in chunk.items():
            print("-----현재 상태 ---------")
            # 현재까지 쌓인 메시지들을 타입과 내용 앞 50글자로 요약 출력
            for msg in state_value:
                print(f"{type(msg).__name__}: {msg.content[:50]}")
            # 이번 단계에서 새로 추가된 마지막 메시지만 자세히 출력
            if state_key == "messages":
                state_value[-1].pretty_print()
            print("=" * 60)


# [스트리밍 - "messages" 모드] LLM이 생성하는 답변을 토큰(글자 조각) 단위로 실시간으로 받음.
# 각 항목은 (메시지 조각, 메타데이터) 튜플. 메타데이터에는 어느 노드에서 나왔는지 등의 정보가 있음
# ChatGPT처럼 글자가 하나씩 찍히는 UI를 만들 때 사용
# (print가 줄바꿈을 하므로 여기선 토큰이 한 줄씩 출력됨)
def stream_messages():
    response = graph.stream(
        {
            "messages": ["Langgraph가 무엇인가요?"]
        },
        stream_mode= "messages"
    )

    for token, metadata in response:
        print(token.content)


# [비동기 스트리밍] stream()과 같은 "updates" 모드를 async for로 받음
async def astream():
    response = graph.astream(
        {
            "messages": ["Langgraph가 무엇인가요?"]
        }
    )
    async for chunk in response:
        for node, state in chunk.items():
            print("---", node, "----")
            print(state)
            print("="*60)

# 직접 실행할 때: 주석을 풀고 원하는 함수로 바꿔서 실행
# 동기 함수는 그냥 invoke() / stream() 처럼 호출, async 함수는 asyncio.run(...)으로 호출
# if __name__ == "__main__":
#     import asyncio
#     asyncio.run(ainvoke())
