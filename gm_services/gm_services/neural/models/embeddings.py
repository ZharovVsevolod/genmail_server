import requests

from ...config import Settings

from langchain_core.embeddings import Embeddings
from ...config import EMBEDDINGS_MODEL_TYPE


class EmbeddingsCall(Embeddings):
    def __init__(self, model_name: EMBEDDINGS_MODEL_TYPE) -> None:
        self.model_name = model_name

        self.host = ...
        self.port = ...
        self.address = f"http://{self.host}:{self.port}"


    def _embed(self, texts: list[str]) -> list[list[float]]:
        # Here is an api call
        task_adress = self.address + "/embed"
        task_params = {
            "model_name": self.model_name,
            "texts": texts
        }
        
        result = requests.get(
            url = task_adress,
            params = task_params
        )
        result = result.json()
        
        return result


    def embed_query(self, text: str) -> list[float]:
        return self._embed([text])[0]
    
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self._embed(texts)
