from pydantic import BaseModel
from typing import Literal, Any, Type


VAR_TYPES = Literal[
    "varchar",
    "integer",
    "date",
    "float",
    "boolean"
]

class TableField(BaseModel):
    name: str
    vartype: VAR_TYPES
    vartype_capacity: int | None = None
    primal_key: bool = False
    could_be_null: bool = True


class BaseTable(BaseModel):
    name: str
    fields: list[TableField]
    output_class: Type[BaseModel]

    def _get_fields_names(self) -> list[str]:
        names = []
        for field in self.fields:
            names.append(field.name)
        return names


    def create_command(self) -> str:
        """
        Make an SQL command for table creation

        It will dynamicly apply all fileds that was described

        Returns
        -------
        command: str
            SQL query
        """
        # Create table of this name
        command = f"CREATE TABLE IF NOT EXISTS {self.name}(\n"

        for field in self.fields:
            # Get capacity of this type if needed
            complex_type = field.vartype
            if field.vartype_capacity is not None:
                complex_type += f"({field.vartype_capacity})"

            # Create column of this name and this type
            param_creation_line = f"    {field.name} {complex_type}"
            # If it is primal key
            if field.primal_key:
                param_creation_line += " PRIMARY KEY"
            # If it can be null
            if not field.could_be_null:
                param_creation_line += " NOT NULL"
            # Add comma for adding next column
            param_creation_line += ",\n"

            command += param_creation_line

        # Remove last comma
        command = command[:-2] + "\n"

        # Close bracket
        command += ");"
        return command


    def insert_values_command(self, values: dict[str, Any]) -> str:
        """
        Make an SQL command for insertion in table

        Arguments
        ---------
        values: dict[str, Any]
            This is a dictionary of row with keys as names of columns
            and values as values of columns

        Returns
        -------
        command: str
            SQL query
        """
        # Insert into specific table
        command = f"INSERT INTO {self.name} ("

        # Add column names
        for key in values.keys():
            command += f"{key}, "
        # Remove last comma and close bracket
        command = command[:-2] + ")\n"

        # Add values of row
        command += "VALUES ("
        for key in values.keys():
            value = values[key]
            if isinstance(value, str):
                value = f"'{value}'"

            command += f"{value}, "
        # Remove last comma and close bracket
        command = command[:-2] + ")"

        return command


    def transform_output(
        self, 
        rows: list[tuple], 
        return_dict: bool = False
    ) -> list[BaseModel | dict]:
        """Transform output from Postgres to pydantic specific class"""
        result: list[BaseModel] = []
        names = self._get_fields_names()

        for row in rows:
            values = list(row)
            # Check if number of columns is correct
            if len(names) != len(values):
                err_msg = f"Lenght of result ({len(values)})"
                err_msg += f"doesn't match with lenght of class ({len(names)})"
                assert KeyError(err_msg)

            # Make output to dict
            data = dict(zip(names, values))

            if return_dict:
                result.append(data)
            else:
                # Make dict to pydantic class that was specified
                result.append(self.output_class.model_validate(data))

        return result