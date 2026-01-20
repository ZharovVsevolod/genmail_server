from .base import BaseTable, TableField
from pydantic import BaseModel


class PassTable(BaseModel):
    user_id: str
    password: str

    @property
    def key_id(self):
        return self.user_id


PASSWORDTABLE = BaseTable(
    name = "userpass",
    fields = [
        TableField(
            name = "user_id",
            vartype = "varchar",
            vartype_capacity = 16,
            primal_key = True
        ),

        TableField(
            name = "password",
            vartype = "varchar",
            vartype_capacity = 20,
            could_be_null = False
        )
    ],
    output_class = PassTable
)