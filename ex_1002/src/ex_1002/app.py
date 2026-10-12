def main() -> None:
    print("app파일")

    # from .mypy import ex_match
    # from .mypy import ex_function
    # from .mypy import ex_oop

    #from .mygraph import test_graph

    #from .mygraph import llm_bind_tools
    
    #import asyncio
    #from .mygraph import search_chatbot_graph
    #asyncio.run(search_chatbot_graph.ainvoke())
    #asyncio.run(search_chatbot_graph.astream())

    #from .mygraph import python_exec_agent
    #python_exec_agent.run()
    #python_exec_agent.run2()

    #from .mygraph import middleware_dynamic_model
    #middleware_dynamic_model.run()

    from .mygraph import middleware_filter_prompt
    middleware_filter_prompt.run()