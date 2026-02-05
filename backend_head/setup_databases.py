from gm_services.loader.load_files_vectorbase import(
    load_data_for_vectorstore_from_folder
)
from gm_services.database.tablestore.pg_creation import (
    create_users_table,
    create_pass_table,
    create_position_table,
    create_user_position_table
)
from src.head import HEAD
from gm_services.config import Settings

from typing import Literal

from dotenv import load_dotenv

import logging
logger = logging.getLogger(__name__)


# Vectorstore paths
## Reference emails for answer generation
PATH_TO_REFERENCE = "data/mail/for_vectorstore/"
## Path to QA Knowledge docs
PATH_TO_KNOWLEDGE_PREPARED = "data/vectorbase/prepared/"
PATH_TO_KNOWLEDGE_NONPREPARED = "data/vectorbase/non_prepared/"

# Tablestore paths
PATH_TO_USER_TABLE = "data/tablestore/users.csv"
PATH_TO_PASS_TABLE = "data/tablestore/passes.csv"
PATH_TO_POSITION_TABLE = "data/tablestore/positions.csv"
PATH_TO_USER_POSITION_TABLE = "data/tablestore/user_postions.csv"


def setup_vectorbase() -> None:
    # Delete previous data
    HEAD.vector_base.delete_index(Settings.services.vectorbase.docs_index)

    # Reference documents
    documents = load_data_for_vectorstore_from_folder(
        path_to_dir = PATH_TO_REFERENCE, 
        source = "reference"
    )
    logger.info("Reference documents count: %d", len(documents))
    HEAD.vector_base.add_documents(documents)

    # Knowledge documents (prepared)
    documents = load_data_for_vectorstore_from_folder(
        path_to_dir = PATH_TO_KNOWLEDGE_PREPARED, 
        source = "knowledge",
        need_splitter = True,
        splitter_type = "standard"
    )
    logger.info("Knowledge prepared documents count: %d", len(documents))
    HEAD.vector_base.add_documents(documents)

    # Knowledge documents (prepared)
    documents = load_data_for_vectorstore_from_folder(
        path_to_dir = PATH_TO_KNOWLEDGE_NONPREPARED, 
        source = "knowledge",
        need_splitter = True,
        splitter_type = "recursive",
        need_to_cut_out_questions = True
    )
    logger.info("Knowledge non-prepared documents count: %d", len(documents))
    HEAD.vector_base.add_documents(documents)


def setup_tablebase() -> None:
    created = create_users_table(PATH_TO_USER_TABLE)
    if created:
        logger.info("User table was created")
    else:
        logger.info("User table was not created")
    
    created = create_pass_table(PATH_TO_PASS_TABLE)
    if created:
        logger.info("Password table was created")
    else:
        logger.info("Password table was not created")
    
    created = create_position_table(PATH_TO_POSITION_TABLE)
    if created:
        logger.info("Position table was created")
    else:
        logger.info("Position table was not created")
    
    created = create_user_position_table(PATH_TO_USER_POSITION_TABLE)
    if created:
        logger.info("User's position table was created")
    else:
        logger.info("User's position table was not created")


def main(mode: Literal["all", "vectorbase", "tablebase"]) -> None:
    if mode in ["all", "vectorbase"]:
        logger.info("Vectorbase setup starting...")
        setup_vectorbase()
        logger.info("Vectorbase setup completed")
    
    if mode in ["all", "tablebase"]:
        logger.info("Tablebase setup starting...")
        setup_tablebase()
        logger.info("Tablebase setup completed")



if __name__ == "__main__":
    load_dotenv()
    main(mode = "all")