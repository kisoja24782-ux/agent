# mygraph 폴더 정리

LangChain / LangGraph로 **도구(tool)를 쓰는 에이전트**를 단계별로 만들어 보는 예제 모음입니다.
파일들은 대략 아래 순서로 난이도가 올라갑니다.

| 단계 | 파일 | 한 줄 요약 |
|---|---|---|
| 1 | [test_graph.py](test_graph.py) | LLM 없이 가장 단순한 LangGraph 그래프 (START → mock_llm → END) |
| 2 | [llm_bind_tools.py](llm_bind_tools.py) | `bind_tools`로 LLM에 도구를 알려주고 `tool_calls`가 어떻게 나오는지 확인 |
| 3 | [search_chatbot_graph.py](search_chatbot_graph.py) | StateGraph를 직접 조립한 **검색 챗봇** (도구 노드 직접 구현) |
| 4 | [coding_agent.py](coding_agent.py) + [python_exec_agent.py](python_exec_agent.py) | `create_agent`로 만든 **파이썬 코드 실행 에이전트** |
| 5 | [middle_cal.py](middle_cal.py) | 미들웨어 예제에서 공용으로 쓰는 계산기 도구 |
| 6 | [middleware_dynamic_model.py](middleware_dynamic_model.py) | `@wrap_model_call` 미들웨어로 **모델을 동적으로 교체** |
| 7 | [middleware_filter_prompt.py](middleware_filter_prompt.py) | `@before_model`(금지어 필터) + `@dynamic_prompt`(말투 랜덤) 미들웨어 |

기타 파일

- [graph.md](graph.md) : `test_graph.py`가 출력한 Mermaid 그래프 그림
- `middleware_wrap_model_call.png`, `middleware_with_node.png` : 미들웨어 예제가 저장한 그래프 이미지
- [langgraph.json](langgraph.json) : LangGraph 서버(`langgraph dev`) 설정. `agent` 그래프로 `search_chatbot_graph.py`의 `graph`를 등록
- `tool_definition.ipynb` : 도구 정의 실습 노트북

---

## 공통 개념

- **도구(tool)** : `@tool` 데코레이터를 붙인 파이썬 함수. 함수 이름·docstring·타입 힌트가 그대로 LLM에게 전달되는 "도구 설명서"가 됩니다.
- **bind_tools** : LLM에게 "이런 도구를 쓸 수 있어"라고 알려주는 것. LLM은 도구를 **직접 실행하지 않고**, 응답의 `tool_calls`에 "어떤 도구를 어떤 인자로 불러줘"라고 적기만 합니다. 실제 실행은 도구 노드가 합니다.
- **State / messages** : 그래프의 모든 노드가 공유하는 상태. `messages`에 `add_messages` 리듀서가 붙어 있어서 노드가 반환한 메시지가 **덮어쓰기가 아니라 뒤에 이어 붙여집니다.** 문자열을 넣으면 자동으로 `HumanMessage`가 됩니다.
- **에이전트 루프** : 거의 모든 예제가 아래 흐름을 따릅니다.

```
사용자 질문 → [model] ──tool_calls 있음──▶ [tools] ─┐
                 ▲                                   │
                 └───────── 도구 결과(ToolMessage) ───┘
              tool_calls 없음 → 최종 답변 → END
```

- 실행에 필요한 API 키(`OPENAI_API_KEY`, `TAVILY_API_KEY`)는 `load_dotenv()`로 `.env`에서 읽습니다.

---

## 1. test_graph.py — 가장 단순한 그래프

```
START → mock_llm → END
```

- `MessagesState`(messages 하나만 있는 기본 State)를 사용합니다.
- `mock_llm` 노드는 실제 LLM을 부르지 않고 항상 `"hello world"` AI 메시지를 반환합니다.
- `graph.invoke(...)` 후 마지막 메시지 내용을 출력하고, `draw_mermaid()`로 그래프 구조를 Mermaid 텍스트로 출력합니다. 이 출력이 [graph.md](graph.md)입니다.
- 모듈 최상단에서 바로 실행되므로 **import만 해도 실행**됩니다.

## 2. llm_bind_tools.py — bind_tools 동작 확인

- `add`, `multiply` 두 도구를 만들고 `ChatOpenAI(model="gpt-4o").bind_tools(tools)`로 연결합니다.
- `"안녕하세요"`처럼 도구가 필요 없는 질문 → `tool_calls`가 **빈 리스트** `[]`로 나옵니다.
- (주석 처리된) `"3 곱하기 5는? 2 더하기 4는?"` 질문 → `multiply`, `add` **두 개의 tool_call**이 한 번에 나오는 것을 확인할 수 있습니다.
- 도구를 실제로 실행하지는 않습니다. "LLM은 호출 요청만 한다"는 점을 보여주는 예제입니다.
- 참고: 이 파일에는 `load_dotenv()`가 없어서 환경변수에 `OPENAI_API_KEY`가 미리 설정돼 있어야 합니다.

## 3. search_chatbot_graph.py — 직접 조립한 검색 챗봇

`StateGraph`로 노드와 엣지를 **직접** 붙여서 에이전트 루프를 만든 예제입니다. 파일 안에 주석이 자세히 달려 있습니다.

```
START → chatbot ──(tool_calls 있음)──▶ tools ──▶ chatbot
           │
           └──(tool_calls 없음)──▶ END
```

| 구성요소 | 역할 |
|---|---|
| `TavilySearch(max_results=3)` | 웹 검색 도구 |
| `State` | `messages: Annotated[list, add_messages]` |
| `chatbot` 노드 | 지금까지의 대화를 `llm_with_tools`에 넘겨 AIMessage를 받아 추가 |
| `BasicToolNode` (`tools` 노드) | 마지막 AIMessage의 `tool_calls`를 하나씩 실행 → 결과를 `ToolMessage`(JSON, `tool_call_id` 포함)로 추가. LangGraph 내장 `ToolNode`를 직접 구현해본 것 |
| `route_tools` | 조건부 엣지. 마지막 메시지에 `tool_calls`가 있으면 `"tools"`, 없으면 `END` |
| `add_edge("tools", "chatbot")` | 도구 실행 후 항상 chatbot으로 복귀 → 루프 형성 |

메시지가 쌓이는 순서 예시:
`HumanMessage → AIMessage(tool_calls) → ToolMessage(검색 결과) → AIMessage(최종 답변)`

같은 그래프를 여러 방식으로 실행하는 함수들:

| 함수 | 방식 | 받는 데이터 |
|---|---|---|
| `invoke()` | 동기, 한 번에 | END까지 돈 뒤 최종 State 전체 |
| `ainvoke()` | 비동기 | invoke와 동일 (`asyncio.run(ainvoke())`) |
| `stream()` | `stream_mode="updates"`(기본) | 노드가 끝날 때마다 `{노드이름: 그 노드가 추가한 값}` |
| `stream_values()` | `stream_mode="values"` | 매 단계 **State 전체** (메시지 리스트가 점점 길어짐) |
| `stream_messages()` | `stream_mode="messages"` | LLM 답변을 **토큰 단위**로 `(조각, 메타데이터)` |
| `astream()` | 비동기 updates | stream과 동일, `async for` |

파일 하단의 `if __name__ == "__main__":`이 주석 처리되어 있으므로, 직접 실행하려면 주석을 풀고 원하는 함수를 호출해야 합니다.
또한 `langgraph.json`에 이 파일의 `graph`가 등록되어 있어 `langgraph dev`로 LangGraph Studio에서 띄울 수 있습니다.

## 4. coding_agent.py + python_exec_agent.py — 코드 실행 에이전트

### coding_agent.py (도구 정의만 있음)

- `python_exec_tool(imports, code)` : `exec()`로 파이썬 코드를 실행합니다.
  1. 먼저 `imports`만 실행해 임포트 실패를 따로 잡고
  2. `imports + code`를 함께 실행합니다.
  3. 성공하면 "성공적으로 실행되었습니다" + 실행한 코드를, 실패하면 에러 메시지를 반환합니다.
- `file_write_tool(file_path, content)` : 파일을 만들어 내용을 씁니다.
- 인자 설명은 pydantic `Field(description=...)`로 붙여 LLM이 각 인자의 의미를 알 수 있게 했습니다.

### python_exec_agent.py (에이전트 실행)

- `create_agent(llm, tools)` 한 줄로 3번에서 손으로 만든 "model ↔ tools 루프"를 자동으로 만들어 줍니다.
- `run()` : "피보나치 수열 코드 작성" 요청 → LLM이 `python_exec_tool`을 호출해 실행해 보고 답합니다.
- `run2()` : "작성 → 실행 확인 → .py 파일로 저장"까지 요청합니다.
- `stream()`으로 노드별(`model`, `tools`) 진행 상황을 출력합니다.

## 5. middle_cal.py — 공용 계산기 도구

- `calculator(a, b, operation)` : `add / subtract / multiply / divide` 지원, 0으로 나누기 처리 포함.
- `tools = [calculator]`를 6·7번 미들웨어 예제가 import해서 씁니다.

## 6. middleware_dynamic_model.py — 모델 동적 교체 (`@wrap_model_call`)

- `@wrap_model_call` 미들웨어는 **모델을 호출하는 순간을 감싸는** 방식입니다. 그래프에 새 노드가 생기지 않습니다.
- `dynamic_model_selection` :
  - 현재 메시지 수가 **10개 이하** → `gpt-4o-mini`
  - **10개 초과** → `gpt-4o`
  - `request.override(model=...)`로 모델만 바꿔 `handler`(원래 모델 호출)에 넘깁니다.
- `run()` :
  1. 그래프 이미지를 `middleware_wrap_model_call.png`로 저장
  2. `MemorySaver` 체크포인터 + 같은 `thread_id`로 6턴 대화 → 메시지가 계속 누적됨
  3. 한 턴에 보통 `Human → AI(tool_call) → Tool → AI` 4개가 쌓이므로, 대화가 이어질수록 메시지 수가 10을 넘어 고급 모델로 전환되는 것을 로그로 확인할 수 있습니다.

## 7. middleware_filter_prompt.py — 입력 필터 + 동적 프롬프트

미들웨어 두 개를 함께 등록합니다.

| 미들웨어 | 종류 | 동작 | 그래프 노드 |
|---|---|---|---|
| `content_filter_middleware` | `@before_model` | 모델 호출 **전에** 마지막 메시지를 검사. `BLOCKED_WORDS`(바보, 멍청이, 나쁜말)가 있으면 `ValueError`로 중단 | **노드가 추가됨** |
| `random_tone_prompt` | `@dynamic_prompt` | 모델 호출마다 시스템 프롬프트를 존댓말/반말 중 랜덤으로 선택 | 추가 안 됨 (wrap_model_call 기반) |

- `run()` :
  1. 그래프 이미지를 `middleware_with_node.png`로 저장 (before_model 노드가 그림에 보임 → 6번 이미지와 비교 포인트)
  2. 테스트 1: 정상 입력 `"15와 7을 더해주세요"` → 계산 결과 출력
  3. 테스트 2: `"바보야 10과 5를 더해"` → 필터에서 `ValueError` 발생 → `차단됨` 출력

---

## 실행 방법

패키지 경로(`ex_1002.mygraph...`)로 import하는 파일이 있으므로 `ex_1002` 프로젝트 루트에서 모듈로 실행하는 것을 권장합니다.

```bash
cd ex_1002
uv run python -m ex_1002.mygraph.test_graph
uv run python -m ex_1002.mygraph.search_chatbot_graph   # 하단 __main__ 주석 해제 필요
uv run python -m ex_1002.mygraph.python_exec_agent
uv run python -m ex_1002.mygraph.middleware_dynamic_model
uv run python -m ex_1002.mygraph.middleware_filter_prompt

# LangGraph Studio (루트의 langgraph.json 사용)
uv run langgraph dev
```

---

## 참고: 코드에서 눈에 띄는 점

- **python_exec_agent.py** : `if __name__ == "__main__":` 블록이 두 개라 직접 실행하면 `run()`과 `run2()`가 **둘 다** 실행됩니다. 또 `run2()`는 파일 저장을 요청하지만 에이전트에 `python_exec_tool`만 등록되어 있어 `file_write_tool`을 쓸 수 없습니다 (`tools`에 추가해야 함).
- **coding_agent.py** : `print()` 결과가 터미널에만 찍히고 도구의 반환값에는 들어가지 않습니다. 그래서 LLM은 실행 결과값을 보지 못하고 "성공했다"는 사실만 압니다. 결과를 LLM에게 돌려주려면 `contextlib.redirect_stdout`으로 출력을 캡처해 반환하면 됩니다. 또한 `exec()`는 임의 코드를 그대로 실행하므로 실습용으로만 사용해야 합니다.
- **mygraph/langgraph.json** : 경로가 `./src/ex_1002/mygraph/...` 기준이라 프로젝트 루트에 있을 때만 맞습니다. 실제로 쓰이는 것은 `ex_1002/langgraph.json`입니다.
- **test_graph.py, llm_bind_tools.py** : 코드가 모듈 최상단에서 실행되므로 다른 파일에서 import하면 바로 실행(및 API 호출)됩니다.
