"""
The specification and load for the yaml config file. It is using OmegaConf for yaml hierarchical structure.

Most of the time you'll need the `Settings` variable with configuration specification.

You can run this .py file to print the config file and check if it is loaded correctly.
"""

from pathlib import Path
from pydantic import BaseModel
from omegaconf import OmegaConf, DictConfig
from os import getcwd
import os.path

from typing import Literal
from dotenv import load_dotenv

import logging

logger = logging.getLogger(__name__)


load_dotenv(os.path.join(getcwd(), ".env"))


# Typing parameters
LLM_MODEL_TYPE = Literal[
    "qwen3:14b", "qwen3:1.7b", "qwen3:8b", "qwen3:4b", "gpt-oss:20b-cloud"
]
EMBEDDINGS_MODEL_TYPE = Literal["FRIDA", "e5-large"]
DEVICE_TYPE = Literal["cpu", "cuda", "mps"]
LLM_ANSWER_PARSER_TYPE = Literal["none", "json", "string"]

DOCUMENT_SESSION_ID_PLACEHOLDER = "NEW_DOCUMENT"


# Get the path to the yaml config file
pwd = getcwd()
config_file = os.path.join(pwd, "config", "config.yaml")


# ---------------------------------
# The whole configuration structure
# ---------------------------------
class Docs(BaseModel):
    main_dir: str
    mail_dir_path: str
    final_name: str

    @property
    def full_mail_path(self) -> str:
        return self.main_dir + self.mail_dir_path

    @property
    def full_final_path(self) -> str:
        return self.main_dir + self.final_name


class System(BaseModel):
    silent: bool
    logging_file: str | None
    # LEVELS: 10 - Debug, 20 - Info, 30 - Warning, 40 - Error, 50 - Critical Error
    logging_level: Literal[10, 20, 30, 40, 50]
    device: DEVICE_TYPE
    server: bool


class BaseService(BaseModel):
    base_url: str


class AllIndexes(BaseModel):
    message_history: str
    documents: str
    document_info: str
    chats: str
    prompt_library: str
    context: str

class Vectorbase(BaseService):
    certs_path: str
    indexes: AllIndexes


class Graphbase(BaseService):
    pass


class LLmEngine(BaseService):
    pass


class Tablebase(BaseService):
    pass


class ServiceOfDocuments(BaseService):
    pass

class RetrieverService(BaseService):
    pass


class Services(BaseModel):
    vectorbase: Vectorbase
    graphbase: Graphbase
    llm_engine: LLmEngine
    tablebase: Tablebase
    document_handler: ServiceOfDocuments
    retriever: RetrieverService


class Models(BaseModel):
    embeddings: EMBEDDINGS_MODEL_TYPE
    llm: LLM_MODEL_TYPE
    thinking_mode: bool
    tools: bool
    prompts_path: str
    language: Literal["ru", "en"]

    @property
    def full_prompts_path(self) -> str:
        return self.prompts_path + self.language + "/"


class SomeApiSettings(BaseModel):
    port: int
    host: str


class ListOfApi(SomeApiSettings):
    main_back: SomeApiSettings
    document_handler: SomeApiSettings
    embeddings_model: SomeApiSettings
    retriever: SomeApiSettings


class Web(BaseModel):
    run_name: str


class Config(BaseModel):
    system: System
    services: Services
    docs: Docs
    models: Models
    api: ListOfApi
    web: Web


# Load the yaml config file
def _load_yaml_config(path: Path) -> DictConfig:
    """Load the yaml config file from the specific path.

    This function using OmegaConf for yaml hierarchical structure opportunity.

    Arguments
    ---------
    path: Path
        Path to the .yaml config file

    Returns
    -------
    config: DictConfig
        The config dictionary

    Raises
    ------
    FileNotFoundError
        If there is no .yaml config file in provided path
    """
    try:
        return OmegaConf.load(path)

    except FileNotFoundError as error:
        message = f"Error! There is no yaml file in {path}"
        logger.exception(message)
        raise FileNotFoundError(error, message) from error


Settings = Config(**_load_yaml_config(config_file))


# Set logging point
logging.basicConfig(
    filename=Settings.system.logging_file,
    level=Settings.system.logging_level,
    encoding="utf-8",
)


if __name__ == "__main__":
    # We can run this .py file to check if the Settings was loaded correctly
    print(Settings.model_dump_json(indent=2))
