# src/file_handler.py
import os
from typing import List, Dict

class FileHandler:
    def __init__(self, directory: str):
        if not os.path.isdir(directory):
            raise ValueError(f"The specified directory does not exist: {directory}")
        self.directory = directory

    def read_markdown_files(self) -> List[Dict[str, str]]:
        documents = []
        for filename in os.listdir(self.directory):
            if filename.endswith(".md"):
                filepath = os.path.join(self.directory, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        documents.append({"filename": filename, "content": content})
                except Exception as e:
                    print(f"Could not read file {filename}: {e}")
        return documents
