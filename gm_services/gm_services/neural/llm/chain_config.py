def make_config_for_chain(
    session_id: str,
    graphbase = None,
    vectorbase = None
) -> dict:
    """Config for runnable_chain.

    Contains everything that llm may need due process.

    **Note**: There is no currently graphbase, so it should be None
    """
    chain_config = {
        "configurable": {
            "session_id": session_id,
            "graphbase": graphbase,
            "vectorbase": vectorbase
        }
    }
    return chain_config
