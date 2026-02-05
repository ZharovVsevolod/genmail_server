from fastapi import FastAPI

from ..osdb_retriever import MAIN_RETRIEVER

from gm_services.schemas.retriever_schemas import (
    FILTER_TYPES,
    RetrieverAnswer
)

app = FastAPI()


@app.get("/retrieve")
def retrieve_similarity(
    query: str,
    k: int = 3,
    filter_type: FILTER_TYPES | None = None,
    what_to_filter: str | None = None,
) -> RetrieverAnswer:
    result = MAIN_RETRIEVER.similarity_search(
        query = query,
        k = k, 
        filter_type = filter_type,
        what_to_filter = what_to_filter
    )
    return result