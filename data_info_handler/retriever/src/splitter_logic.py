import re
from uuid import uuid4

from langchain_text_splitters import (
    CharacterTextSplitter, 
    RecursiveCharacterTextSplitter
)

from langchain_core.documents import Document
from langchain_text_splitters.base import TextSplitter
from typing import Literal, Union, Optional


def preprocess_re(text: str) -> str:
    """Clean text from trash symbols"""
    cleaned_text = re.sub(r"[^а-яёА-Я-Z0-9.,\n \-:!;?\[\]\(\)]", "", text)
    cleaned_text = re.sub(r"[`*~{}=<>##§]", " ", cleaned_text)
    cleaned_text = re.sub(r"\/\/\.\.", " ", cleaned_text)
    cleaned_text = re.sub(r"([а-я])-\s+([а-я])", r"\1\2", cleaned_text)
    cleaned_text = re.sub(r"\n", " ", cleaned_text)
    cleaned_text = re.sub(r"\s+ ", " ", cleaned_text)

    return cleaned_text


def get_standard_splitter(separator: str = "\n\n") -> CharacterTextSplitter:
    """Return standard CharacterTextSplitter 
    (for documents with prepared structure)
    """
    text_splitter = CharacterTextSplitter(
        separator = separator,
        chunk_size = 100,
        chunk_overlap = 0,
        length_function = len,
        is_separator_regex = False
    )

    return text_splitter


def get_recursive_splitter(
    chunk_size: int = 420, 
    chunk_overlap: int = 50
) -> RecursiveCharacterTextSplitter:
    """Return RecursiveCharacterTextSplitter 
    (for documents with non-prepared structure)
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = chunk_size,
        chunk_overlap = chunk_overlap,
        length_function = len,
        is_separator_regex = False,
    )

    return text_splitter


def load_and_split_file(
    path_to_file: str, 
    source_name: str, 
    splitter_type: Optional[Union[Literal["standard", "recursive"], TextSplitter]] = None,
    need_to_cut_out_questions: bool = False
) -> list[Document]:
    """Load document and cut to text chunks

    Arguments
    ---------
    path_to_file: str
        Path to document that needed to be splitted to chunks
    
    source_name: str
        Name of the document - for metadata
    
    splitter_type: Literal["standard", "recursive"] | TextSplitter | None
        Splitter type or splitter itself.\n
        Type could be:\n
            - "standard" - for prepared documents
            - "recursive" - for non-prepared documents
    
        if None - will be default "recursive" type.
    
    need_to_cut_out_questions: bool = False
        If need to cut some questions in text (for textbooks manually).
    """
    if splitter_type is None:
        splitter_type = "recursive"
    
    match splitter_type:
        case "recursive":
            splitter = get_recursive_splitter()
        
        case "standard":
            splitter = get_standard_splitter()
        
        case _:
            splitter = splitter_type

    with open(path_to_file, encoding = "utf8") as f:
        document_original = f.read()
    
    if splitter_type != "standard":
        document_original = preprocess_re(document_original)

    document_split = splitter.create_documents(
        texts = [document_original],
        metadatas = [{"source": source_name}]
    )

    for doc in document_split:
        doc.metadata["id"] = str(uuid4())

    if need_to_cut_out_questions:
        document_split = [
            chunk for chunk in document_split if "?" not in chunk.page_content
        ]

    return document_split
