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
        for root, _, files in os.walk(self.directory):
            for filename in files:
                if filename.endswith(".md"):
                    filepath = os.path.join(root, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                            # Store original relative path for better identification
                            relative_path = os.path.relpath(filepath, self.directory)
                            documents.append({"filename": relative_path, "content": content})
                    except Exception as e:
                        print(f"Could not read file {filepath}: {e}")
        return documents
