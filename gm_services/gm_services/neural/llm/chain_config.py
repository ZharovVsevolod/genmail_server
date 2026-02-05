from gm_services.database.vectorstore import OpenSearchConnection
from gm_services.clients import RetrieverClient
from typing import TypedDict


class ConfigurableChainConfig(TypedDict):
    session_id: str
    graphbase: None
    vectorbase: OpenSearchConnection
    retriever: RetrieverClient

class ChainConfig(TypedDict):
    configurable: ConfigurableChainConfig


def make_config_for_chain(
    session_id: str,
    graphbase: None = None,
    vectorbase: OpenSearchConnection | None = None,
    retriever: RetrieverClient = None
) -> ChainConfig:
    """Config for runnable_chain.

    Contains everything that llm may need due process.

    **Note**: There is no currently graphbase, so it should be None
    """
    chain_config = {
        "configurable": {
            "session_id": session_id,
            "graphbase": graphbase,
            "vectorbase": vectorbase,
            "retriever": retriever
        }
    }
    return chain_config
