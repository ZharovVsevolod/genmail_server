from .base import BaseTable, TableField
from pydantic import BaseModel


class User(BaseModel):
    id: str
    name: str
    surname: str
    patronymic: str | None
    email: str

    @property
    def key_id(self):
        return self.id


USER = BaseTable(
    name = "users",
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
            name = "surname",
            vartype = "varchar",
            vartype_capacity = 20,
            could_be_null = False
        ),

        TableField(
            name = "patronymic",
            vartype = "varchar",
            vartype_capacity = 20,
            could_be_null = True
        ),

        TableField(
            name = "email",
            vartype = "varchar",
            vartype_capacity = 20,
            could_be_null = False
        )
    ],
    output_class = User
)