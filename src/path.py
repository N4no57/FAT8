from src.directory import find_entry, find_entry_by_cluster
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

def get_full_path(FAT: list[int], start_cluster: int) -> str:
    parts = []
    current_cluster = start_cluster

    if start_cluster == ROOT_DIRECTORY_SECTOR_START:
        return "/"

    while True:
        dotdot_entry = find_entry(FAT, "..", current_cluster)
        parent_cluster = dotdot_entry.first_cluster

        name_entry = find_entry_by_cluster(FAT, current_cluster, parent_cluster)
        parts.append(name_entry.filename)

        current_cluster = parent_cluster

        if parent_cluster == ROOT_DIRECTORY_SECTOR_START:
            break

    parts.reverse()
    return "/" + "/".join(parts)

def is_absolute(path: str) -> bool:
    return path.startswith('/')