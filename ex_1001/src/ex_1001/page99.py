from langchain_core.messages import AIMessage, HumanMessage, AnyMessage
from langgraph.graph.message import add_messages
from typing import TypedDict, Annotated

msgs1 = [HumanMessage(content="Hello", id="1")]
msgs2 = [AIMessage(content="Hi there", id="2")]

#print(add_messages(msgs1, msgs2))


# 1oo page
class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]

state: State={
    "messages": add_messages(msgs1, msgs2)
}

print(state["messages"])