from src.directory import list_directory
from src.path import resolve, get_full_path

def cmd_help():
    pass

def cmd_cd(FAT: list[int], directory: str, cwd_cluster: int) -> (str, int):
    dir_entry = resolve(FAT, directory, cwd_cluster)

    directory_path = get_full_path(FAT, dir_entry.first_cluster)

    return directory_path, dir_entry.first_cluster

def cmd_ls(FAT: list[int], cwd_cluster: int) -> None:
    list_directory(FAT, cwd_cluster)