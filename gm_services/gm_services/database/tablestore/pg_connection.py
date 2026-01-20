import os
import psycopg2

from .table_schemas.password import PASSWORDTABLE
from .table_schemas.user import USER
from .table_schemas.user_position import USERPOSITIONTABLE
from .table_schemas.position import POSITIONTABLE
from ....config import Settings

from .table_schemas.password import PassTable
from .table_schemas.user import User
from .table_schemas.base import BaseTable

import logging
logger = logging.getLogger(__name__)


class PGHandler:
    def __init__(self) -> None:
        self.pgs = psycopg2.connect(
            database = os.environ["POSTGRES_DB_NAME"],
            user = os.environ["POSTGRES_USER"],
            password = os.environ["POSTGRES_PASSWORD"],
            host = Settings.services.tablebase.base_url,
            port = 5432
        )
    

    def _execute_sql(
        self, 
        query: str,
        need_to_return: bool = False
    ) -> None | list[tuple]:
        cursor = self.pgs.cursor()
        cursor.execute(query)
        
        # Return all rows if needed to return something
        if need_to_return:
            return cursor.fetchall()
        
        # Commit changes to database if they were
        self.pgs.commit()
        
        cursor.close()
        logger.info("Query was commited successfully")


    def check_password(self, user_id: str, user_password: str) -> bool:
        try:
            query = f"SELECT * FROM {PASSWORDTABLE.name} "
            query += f"WHERE user_id='{user_id}'"

            result = self._execute_sql(query, need_to_return = True)
            result: PassTable = PASSWORDTABLE.transform_output(result)[0]

            if result.password == user_password:
                return True
            else:
                return False
        
        # If something went wrong - then password didn't match
        except:
            return False
    

    def find_user(self, user_id: str, return_dict: bool = False) -> User | None:
        """Return `User` if there is a match, or `None` if nothing was found"""
        try:
            query = f"SELECT * FROM {USER.name} "
            query += f"WHERE id='{user_id}'"
            result = self._execute_sql(query, need_to_return = True)

            result: User = USER.transform_output(result, return_dict)[0]
            return result
        
        except:
            return None


    def create_table(self, table: BaseTable) -> None:
        command = table.create_command()
        self._execute_sql(command)
    

    def insert_values_to_table(self, table: BaseTable, values: dict) -> None:
        for value in values:
            command_for_insert_row = table.insert_values_command(value)
            self._execute_sql(command_for_insert_row)
    

    def find_user_position(self, user: User) -> str:
        """Return position name if there is a match, or `None` if nothing was found"""
        try:
            query = f"SELECT {USERPOSITIONTABLE.name}.user_id, {POSITIONTABLE.name}.name "
            query += f"FROM {USERPOSITIONTABLE.name} "
            query += f"INNER JOIN {POSITIONTABLE.name} "
            query += f"ON {USERPOSITIONTABLE.name}.position_id={POSITIONTABLE.name}.id "
            query += f"WHERE {USERPOSITIONTABLE.name}.user_id='{user.key_id}'"
            result = self._execute_sql(query, need_to_return = True)

            _, result = result[0]
            return result
        
        except:
            return None
