from langchain_huggingface.embeddings import HuggingFaceEmbeddings

from gm_services.config import Settings

from gm_services.config import EMBEDDINGS_MODEL_TYPE, DEVICE_TYPE

import logging
logger = logging.getLogger(__name__)


class EmbeddingsHandler:
    def __init__(self, model_name: EMBEDDINGS_MODEL_TYPE) -> None:
        self.model = self._init_embeddings_model(
            model_name = model_name,
            device = Settings.system.device
        )

    def _match_model_path(
        self, 
        model_name: EMBEDDINGS_MODEL_TYPE
    ) -> str:
        match model_name:
            case "FRIDA":
                model_path = "ai-forever/FRIDA"
            
            case "e5-large":
                model_path = "intfloat/multilingual-e5-large-instruct"
        
        return model_path
    
    def _init_embeddings_model(
        self, 
        model_name: EMBEDDINGS_MODEL_TYPE,
        device: DEVICE_TYPE
    ) -> HuggingFaceEmbeddings:
        embeddings_name = self._match_model_path(model_name)

        model = HuggingFaceEmbeddings(
            model_name = embeddings_name,
            model_kwargs = {"device": device}
        )
        return model
    
    def embed(self, texts: list[str]) -> list[list[float]]:
        result = self.model.embed_documents(texts)
        return result



def initialize_all_models() -> dict[EMBEDDINGS_MODEL_TYPE, EmbeddingsHandler]:
    """
    Create all embeddings instances to be able to get access to all of them

    Currently supports this models:
        - FRIDA
    """
    logger.info("Embedding model: FRIDA")
    model_frida = EmbeddingsHandler("FRIDA")

    all_embeddings = {
        "FRIDA": model_frida
    }
    return all_embeddings