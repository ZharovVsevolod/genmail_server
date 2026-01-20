from .base import BaseTable, TableField
from pydantic import BaseModel


class UserPosition(BaseModel):
    user_id: str
    position_id: str

    @property
    def key_id(self):
        return self.user_id


USERPOSITIONTABLE = BaseTable(
    name = "userposition",
    fields = [
        TableField(
            name = "user_id",
            vartype = "varchar",
            vartype_capacity = 16,
            primal_key = True
        ),

        TableField(
            name = "position_id",
            vartype = "varchar",
            vartype_capacity = 20,
            could_be_null = False
        )
    ],
    output_class = UserPosition
)