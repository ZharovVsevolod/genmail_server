import os
import pandas as pd
from tqdm import tqdm


class PandasIndexes:
    def __init__(self):
        self.store: dict[str, pd.DataFrame] = {}

    def create(self, index: str, data: pd.DataFrame | None = None) -> None:
        """Create a new index"""
        if data is None:
            data = pd.DataFrame()
        self.store[index] = data

    def exists(self, index: str) -> bool:
        """Check if index is exists"""
        return self.store.get(index) != None

    def delete(self, index: str) -> None:
        """Delete an index"""
        del self.store[index]



class BasePandasStore:
    def __init__(self, load_path: str | None = None) -> None:
        if load_path is None:
            self.indices = PandasIndexes()
        else:
            self.load()
    

    def save(self, path_to_save_folder: str) -> None:
        """Save current store to local file"""
        # Check if the save path ends with "/"
        if path_to_save_folder[-1] != "/":
            path_to_save_folder += "/"
        
        for key in self.indices.store.keys():
            index = self.indices.store.get(key)
            save_name = path_to_save_folder + key + ".csv"
            index.to_csv(save_name, sep = ";", encoding = "utf-8")
    

    def load(self, path_to_save_folder : str) -> None:
        """Load saved store from folder"""
        self.indices = PandasIndexes()

        files = os.scandir(path_to_save_folder)

        for file in tqdm(files, desc = "Load indices from load path"):
            if file.is_file():
                split_name = file.name.split(".")
                name = "".join(split_name[:-1])
                extension = split_name[-1]

                if extension is "csv":
                    self.indices.create(
                        index = name,
                        data = pd.read_csv(file.path)
                    )


    def search(self):
        """Search for a record in the index"""
        pass


    def index(self, index: str, id: str, body: dict) -> None:
        """Creates or updates record in the index"""
        pass
    

    def update(self, index: str, id: str, body: dict) -> None:
        """Change the record in the index"""
        self.indices.store[index]


    def create(self, index: str, id: str, body: dict) -> None:
        """Add the record to the index"""
        pass


    def delete(self, index: str, id: str) -> None:
        """Delete the record in the index"""
        pass


    def clear(self, index: str) -> None:
        """Clear all records in the index"""
        self.indices.delete(index)
        self.indices.create(index)