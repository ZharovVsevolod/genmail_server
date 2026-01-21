from .table_schemas.user import USER
from .table_schemas.password import PASSWORDTABLE
from .table_schemas.position import POSITIONTABLE
from .table_schemas.user_position import USERPOSITIONTABLE

from ...common import pd_load_from_csv
from .pg_connection import PGHandler

from .table_schemas.base import BaseTable

import logging
logger = logging.getLogger(__name__)


def create_table(
    table: BaseTable, 
    path_to_file: str,
    tablestore: PGHandler | None = None
) -> None:
    if tablestore is None:
        tablestore = PGHandler()

    # Create table
    tablestore.create_table(table)

    # Load data from file
    values_to_insert = pd_load_from_csv(path_to_file, index = False)
    # Convert pd.Dataframe to list of rows (dict type)
    values_to_insert = values_to_insert.to_dict(orient = "records")

    # Insert values
    tablestore.insert_values_to_table(table, values_to_insert)


def create_users_table(path_to_file: str) -> bool:
    """
    Create table (if not exists) for users 
    and fill it with values from file

    File should be `.csv` and contains this columns:
        - id
        - name
        - surname
        - patronymic *(optional)*
        - email

    Parameters
    ----------
    path_to_file: str
        Path to .csv file
    
    Returns
    -------
    if_execution_was_good: bool
        True, if there was no errors. False otherwise
    """
    try:
        create_table(USER, path_to_file)
        return True
    
    except Exception as error:
        logger.exception(error)
        return False


def create_pass_table(path_to_file: str) -> None:
    """
    Create table (if not exists) for user's passwords 
    and fill it with values from file

    File should be `.csv` and contains this columns:
        - user_id
        - password

    Parameters
    ----------
    path_to_file: str
        Path to .csv file
    
    Returns
    -------
    if_execution_was_good: bool
        True, if there was no errors. False otherwise
    """
    try:
        create_table(PASSWORDTABLE, path_to_file)
        return True
    
    except Exception as error:
        logger.exception(error)
        return False


def create_position_table(path_to_file: str) -> None:
    """
    Create table (if not exists) for positions index
    and fill it with values from file

    File should be `.csv` and contains this columns:
        - id
        - name

    Parameters
    ----------
    path_to_file: str
        Path to .csv file
    
    Returns
    -------
    if_execution_was_good: bool
        True, if there was no errors. False otherwise
    """
    try:
        create_table(POSITIONTABLE, path_to_file)
        return True
    
    except Exception as error:
        logger.exception(error)
        return False


def create_user_position_table(path_to_file: str) -> None:
    """
    Create table (if not exists) for user's positions 
    and fill it with values from file

    File should be `.csv` and contains this columns:
        - user_id
        - position_id

    Parameters
    ----------
    path_to_file: str
        Path to .csv file
    
    Returns
    -------
    if_execution_was_good: bool
        True, if there was no errors. False otherwise
    """
    try:
        create_table(USERPOSITIONTABLE, path_to_file)
        return True
    
    except Exception as error:
        logger.exception(error)
        return False
