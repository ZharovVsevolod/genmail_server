from .base import BaseTable, TableField
from pydantic import BaseModel
from typing import Literal


# Role levels
USER_LEVEL: int = 10
DEVELOPER_LEVEL: int = 30
ADMIN_LEVEL: int = 50


class Role(BaseModel):
    id: str
    name: str
    level: Literal[10, 20, 30, 40, 50]

    @property
    def key_id(self):
        return self.id


LEVEL = BaseTable(
    name = "roles",
    fields = [
        TableField(
            name = "id",
            vartype = "varchar",
            vartype_capacity = 16,
            primal_key = True
        ),

        TableField(
            name = "name",
            vartype = "varchar",
            vartype_capacity = 20,
            could_be_null = False
        ),

        TableField(
            name = "level",
            vartype = "integer",
            could_be_null = False
        )
    ],
    output_class = Role
)