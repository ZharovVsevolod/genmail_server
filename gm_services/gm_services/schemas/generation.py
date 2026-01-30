from pydantic import BaseModel


class BaseGenerationBody(BaseModel):
    letter_body: str
    history: list
