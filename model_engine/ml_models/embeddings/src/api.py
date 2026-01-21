from fastapi import FastAPI

from .emb_model import initialize_all_models

from gm_services.gm_services.config import EMBEDDINGS_MODEL_TYPE

import logging
logger = logging.getLogger(__name__)


logger.info("Initializing embedding models")
ALL_EMBEDDINGS = initialize_all_models()
logger.info("Embedding models was initialized")

app = FastAPI()

app.get("/embed")
async def text_to_embeddgins(
    model_name: EMBEDDINGS_MODEL_TYPE,
    texts: list[str]
) -> dict[str, list[list[float]]]:
    """
    Transform batch of text to batch of embeedings via embeddings model

    Arguments
    ---------
    model_name: Literal['FRIDA', 'e5-large']
        Model that will be used to generate embeddings
    
    texts: list[str]
        Batch of texts
    
    Returns
    -------
    result: dict[str, list[list[float]]]
        {"embeddings": batch_of_embeddings}
    """
    result = ALL_EMBEDDINGS.get(model_name).embed(texts)
    return {"embeddings": result}


@app.get("/")
def read_root():
    """Check connection"""
    return {"message": "Wake up, Neo"}


@app.get("/health")
def check_health():
    """Health check"""
    return {"message": "healthy"}