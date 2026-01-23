# TODO: fix (currently no graphbase in gm_services)


def make_config_fot_chain(*args, **kwargs):
    pass


# from ..databases.graphstore import Neo4jHandler
# from ..databases.vectorstore import ElasticHandler


# def make_config_for_chain(
#     session_id: str,
#     graphbase: Neo4jHandler | None = None,
#     vectorbase: ElasticHandler | None = None
# ) -> dict:
#     """Config for runnable_chain.

#     Contains everything that llm may need due process
#     """
#     chain_config = {
#         "configurable": {
#             "session_id": session_id,
#             "graphbase": graphbase,
#             "vectorbase": vectorbase
#         }
#     }
#     return chain_config
