from .base import BaseTable, TableField
from pydantic import BaseModel


class PositionTable(BaseModel):
    id: str
    name: str

    @property
    def key_id(self):
        return self.id


POSITIONTABLE = BaseTable(
    name = "position",
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
        )
    ],
    output_class = PositionTable
)