from typing import Optional

from pydantic import BaseModel


class FileObjectModel(BaseModel):
    """Description load file"""
    start_file_name: str
    file_extension: str
    content_type: str
    hash_file: Optional[str]
    abs_path_directory: Optional[str]
    abs_path: Optional[str]
