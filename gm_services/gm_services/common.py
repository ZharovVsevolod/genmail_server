import os
import pandas as pd
import secrets
import docx
from markdown import Markdown
from io import StringIO
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage

from .config import Settings


def simple_langchain_messages(system: str | None, human: str) -> list[BaseMessage]:
    messages = []

    if system is not None:
        messages.append(SystemMessage(system))
    
    messages.append(HumanMessage(human))

    return messages


def to_json_safe(obj) -> dict:
    match obj:
        case BaseMessage():
            return obj.model_dump()
        case list():
            return [to_json_safe(x) for x in obj]
        case dict():
            return {k: to_json_safe(v) for k, v in obj.items()}

    return obj


def pd_save_to_csv(data: pd.DataFrame, path_to_save: str) -> None:
    if not os.path.exists(path_to_save):
        os.mkdir(path_to_save)
    
    data.to_csv(path_to_save, sep = ";", encoding = "utf-8", index = True, index_label = "id")


def pd_load_from_csv(path_to_load: str, index: bool = True) -> pd.DataFrame:
    if index:
        index_col = 0
    else:
        index_col = False
    
    data = pd.read_csv(
        filepath_or_buffer = path_to_load, 
        sep = ";", 
        header = 0, 
        index_col = index_col, 
        encoding = "utf-8", 
        dtype=str
    )
    return data


def generate_hex(nbytes: int = 16) -> str:
    """New token generation"""
    return secrets.token_hex(nbytes)


def load_prompt(path_to_prompt: str, default_path: bool = False) -> str:
    if default_path:
        path_to_prompt = Settings.models.full_prompts_path + path_to_prompt

    with open(path_to_prompt, encoding = "utf-8") as file:
        result = file.read()
    
    return result


# https://stackoverflow.com/questions/29309085/read-docx-files-via-python
def load_docx_text(filename: str) -> str:
    doc = docx.Document(filename)

    full_text = []
    for paragraph in doc.paragraphs:
        full_text.append(paragraph.text)
    result = "\n".join(full_text)
    
    return result


def cut_thinking_part_of_message(message: str) -> str:
    return message.split("</think>")[1]


# https://stackoverflow.com/questions/761824/python-how-to-convert-markdown-formatted-text-to-text
def unmark_element(element, stream = None):
    if stream is None:
        stream = StringIO()
    if element.text:
        stream.write(element.text)
    for sub in element:
        unmark_element(sub, stream)
    if element.tail:
        stream.write(element.tail)
    return stream.getvalue()

# -----
Markdown.output_formats["plain"] = unmark_element
__md = Markdown(output_format = "plain")
__md.stripTopLevelTags = False
# -----

def unmark(text: str):
    return __md.convert(text)


def delete_file(path: str):
    os.remove(path)