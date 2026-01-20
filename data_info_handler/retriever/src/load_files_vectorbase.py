import os
from pydantic import BaseModel
from langchain_core.documents import Document

from .splitter_logic import load_and_split_file


SUPPORTED_EXTENSIONS = ["txt"]


class FileEntity(BaseModel):
    path: str
    name: str
    
    @property
    def extension(self):
        return self.name.split(".")[-1]


def load_data_for_vectorstore_from_folder(
    path_to_dir: str,
    source: str,
    need_splitter: bool = False,
    **kwargs # for `load_and_split_file` function
) -> list[Document]:
    # Check the end of path - it should be with "/", because it's a path to folder
    if path_to_dir[-1] != "/":
        path_to_dir += "/"

    # Scan directory
    docs = [
        FileEntity(
            path = doc.path,
            name = doc.name
        )
        for doc in os.scandir(path_to_dir)
    ]

    # Remove everything except files with supported extensions
    docs = [doc for doc in docs if doc.extension in SUPPORTED_EXTENSIONS]

    # Load text from files
    texts = []
    for doc in docs:
        doc_path = path_to_dir + doc.name

        match doc.extension:
            case "txt":
                if need_splitter:
                    data = load_and_split_file(
                        path_to_file = doc_path,
                        source_name = source,
                        **kwargs
                    )
                else:
                    with open(doc_path, mode = "r", encoding = "utf-8") as file:
                        data = file.readlines()
                        data = "\n".join(data)
        
        texts.append(data)
    
    if need_splitter:
        # Unsqeeze List[List[Document]] to List[Document]
        documents: list[Document] = []
        for data in texts:
            documents.extend(data)

    else:
        # Transfer pure text to Langchain Document
        documents: list[Document] = [
            Document(
            page_content = text, 
            metadata = {"source": source}
        ) for text in texts]
    
    return documents