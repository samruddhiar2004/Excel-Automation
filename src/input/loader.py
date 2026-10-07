from abc import ABC, abstractmethod
from pathlib import Path
from typing import BinaryIO, List, Optional, Union
import io

class InputItem:
    """Represents a single input file or stream for processing."""
    def __init__(self, source_name: str, content: Union[Path, bytes, BinaryIO]):
        self.source_name = source_name
        self.content = content

    def get_stream(self) -> Union[Path, BinaryIO]:
        if isinstance(self.content, bytes):
            return io.BytesIO(self.content)
        return self.content

class BaseInputSource(ABC):
    """Abstract interface for input sources, allowing future additions (Email, API, Cloud, etc.)"""
    @abstractmethod
    def get_inputs(self) -> List[InputItem]:
        pass

class FileInputSource(BaseInputSource):
    """Input source that collects .xlsx files from local paths."""
    def __init__(self, file_paths: List[Union[str, Path]]):
        self.file_paths = [Path(p) for p in file_paths]

    def get_inputs(self) -> List[InputItem]:
        items: List[InputItem] = []
        for p in self.file_paths:
            if not p.exists():
                raise FileNotFoundError(f"Input file not found: {p}")
            if p.suffix.lower() not in [".xlsx", ".xls"]:
                raise ValueError(f"Unsupported file format: {p.name}. Only .xlsx is supported.")
            items.append(InputItem(source_name=p.name, content=p))
        return items

class UploadedStreamInputSource(BaseInputSource):
    """Input source for in-memory uploaded files (e.g. from Web API)."""
    def __init__(self, uploads: List[tuple[str, bytes]]):
        self.uploads = uploads

    def get_inputs(self) -> List[InputItem]:
        items: List[InputItem] = []
        for filename, data in self.uploads:
            if not filename.lower().endswith((".xlsx", ".xls")):
                raise ValueError(f"Unsupported file format: {filename}. Only .xlsx is supported.")
            items.append(InputItem(source_name=filename, content=data))
        return items
