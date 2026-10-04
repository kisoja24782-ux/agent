def main() -> None:
    print("app파일")

    # from .mypy import ex_match
    # from .mypy import ex_function
    # from .mypy import ex_oop

    #from .mygraph import test_graph

    #from .mygraph import page123
    import asyncio
    from .mygraph import page132

    #asyncio.run(page132.ainvoke())
    asyncio.run(page132.astream())