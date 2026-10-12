from dotenv import load_dotenv

from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

from ex_1002.mygraph.coding_agent import python_exec_tool

load_dotenv()

tools = [python_exec_tool]

llm = ChatOpenAI(model="gpt-4o")
graph = create_agent(llm, tools)






def run():
    response = graph.stream(
        {
            "messages":[
                "첫 번째 항이 1인 피보나치 수열을 출력하는 파이썬 코드를 작성해주세요."
            ]
        }
    )

    for chunk in response:
        for node, value in chunk.items():
            if node:
                print("---", node, "---")
            if "messages" in value:
                print(value['messages'][0].content)


if __name__ == "__main__":
    run()


def run2():
    response = graph.stream(
        {
            "messages":[
                "첫 번째 항이 1인 피보나치 수열을 출력하는 파이썬 코드를 작성해주세요.정상적으로 실행되는지 확인도 해주세요"
                "확인했다면 그 코드는 .py파일로 저장하세요."
                
            ]
        }
    )

    for chunk in response:
        for node, value in chunk.items():
            if node:
                print("---", node, "---")
            if "messages" in value:
                print(value['messages'][0].content)


if __name__ == "__main__":
    run2()