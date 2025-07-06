from src.directory import list_directory, create_directory, delete_directory
from src.path import resolve, get_full_path

def cmd_help():
    pass

def cmd_cd(FAT: list[int], directory: str, cwd_cluster: int) -> (str, int):
    dir_entry = resolve(FAT, directory, cwd_cluster)

    directory_path = get_full_path(FAT, dir_entry.first_cluster)

    return directory_path, dir_entry.first_cluster

def cmd_ls(FAT: list[int], cwd_cluster: int) -> None:
    list_directory(FAT, cwd_cluster)

def cmd_mkdir(FAT: list[int], name: str, cwd_cluster: int) -> None:
    create_directory(FAT, name, cwd_cluster)

def cmd_rm(FAT:list[int], args: list[str], cwd_cluster: int) -> None:
    mode = ""
    file = ""

    i = 0
    while i < len(args):
        if args[i].startswith("-"):
            mode += args[i][1:]
            i+=1
            continue

        file = args[i]
        break

    if 'd' in mode:
        delete_directory(FAT, file, cwd_cluster)