def main() -> None:
    print("app파일")

    #from .rag_agent import retriever
    #retriever.run()

    from .rag_agent import agent
    agent.run()