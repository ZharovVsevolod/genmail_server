from .base import BaseTable, TableField
from pydantic import BaseModel


class RoleTable(BaseModel):
    user_id: str
    role_id: str

    @property
    def key_id(self):
        return self.user_id


PASSWORDTABLE = BaseTable(
    name = "userrole",
    fields = [
        TableField(
            name = "user_id",
            vartype = "varchar",
            vartype_capacity = 16,
            primal_key = True
        ),

        TableField(
            name = "role_id",
            vartype = "varchar",
            vartype_capacity = 20,
            could_be_null = False
        )
    ],
    output_class = RoleTable
)