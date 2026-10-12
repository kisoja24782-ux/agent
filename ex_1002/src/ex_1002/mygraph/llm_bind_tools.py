from langchain_core.tools import tool

@tool
def add(a: int, b:int) -> int:
    """Adds a and b.
    
    Args:
        a : first int
        b : second int
    """

    return a + b

@tool
def multiply(a: int, b: int) -> int:
    """Multiplies a and b.
    Args:
        a : first int
        b : second int
    """
    return a * b

tools = [add, multiply]

from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o")
llm_with_tools = llm.bind_tools(tools)

query = "3 곱하기 5는 뭔가요? 그리고 2 더하기 4는 뭔가요?"

# response = llm_with_tools.invoke(query)
# print(response.tool_calls)


query2 = "안녕하세요"
response2 = llm_with_tools.invoke(query2)
print(response2.tool_calls)