from langchain_core.embeddings import Embeddings
from ...config import EMBEDDINGS_MODEL_TYPE


class EmbeddingsCall(Embeddings):
    def __init__(self, model_name: EMBEDDINGS_MODEL_TYPE) -> None:
        self.model_name = model_name

        # Should get from Settings-config
        self._model_port = ""
    

    def _get_model_port(self) -> str:        
        match self.model_name:
            case "FRIDA":
                return ""

            case "e5-large":
                return ""


    def _embed(self, texts: list[str]) -> list[list[float]]:
        # Here is an api fetch
        pass


    def embed_query(self, text: str) -> list[float]:
        return self._embed([text])[0]
    
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self._embed(texts)
