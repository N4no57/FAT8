from src.fs import DirectoryEntry, read_directory
from src.utils import ROOT_DIRECTORY_SECTOR_START

def resolve(FAT: list[int], path: str, cwd_cluster: int = ROOT_DIRECTORY_SECTOR_START) -> DirectoryEntry:
    """Navigate the path and return the final DirectoryEntry"""
    if is_absolute(path):
        current_cluster = ROOT_DIRECTORY_SECTOR_START
        components = path.lstrip("/").split('/')
    else:
        current_cluster = cwd_cluster
        components = path.split('/')

    match = None
    for index, component in enumerate(components):
        entries = read_directory(FAT, current_cluster)
        for entry in entries:
            if entry.filename.strip() == component:
                match = entry
                break

        if match is None:
            raise FileNotFoundError(f"File {component} not found")

        if index < len(components) - 1:
            if not match.is_directory():
                raise NotADirectoryError(f"Directory {component} not found")
            current_cluster = match.first_cluster
        else:
            return match

    return match

def split_path(path: str) -> (str, str):
    """Split '/foo/bar/baz.txt' into ('/foo/bar', 'baz.txt')"""

def is_absolute(path: str) -> bool:
    return path.startswith('/')