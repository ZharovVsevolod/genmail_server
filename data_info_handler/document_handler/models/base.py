from gm_services.database.tablestore.pg_sqlalchemy_connector import PGHandler


pg_handler = PGHandler()
Base = pg_handler.Base
