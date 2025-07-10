from src.directory import create_entry, find_entry
from src.disk import write_sector, read_sector
from src.fat_table import get_cluster_chain
from src.fs import DirectoryEntry

def read_file(FAT: list[int], file, dir_cluster) -> str:
    """Read a file's contents by following its cluster chain."""
    file_entry = find_entry(FAT, file, dir_cluster)
    if file_entry is None:
        raise FileNotFoundError
    cluster_chain = get_cluster_chain(FAT, file_entry.first_cluster)
    return "".join(read_sector(cluster).decode('ascii').rstrip('\x00') for cluster in cluster_chain)

def write_file(FAT: list[int], name, dir_cluster) -> str:
    """write a file's contents by following its cluster chain."""

def create_file(FAT: list[int], dir_cluster: int, name: str, extension: str, data: bytes) -> bool:
    """Write a new file into a given directory cluster."""
    size = (len(data)//512)+1
    if find_duplicate_file(FAT, dir_cluster, name, extension):
        print("file already exists")
        return False

    file_entry = create_entry(FAT, name, extension,
                              parent_cluster=dir_cluster, size=size)
    cluster_chain = get_cluster_chain(FAT, file_entry.first_cluster)

    chain_num = 0
    for i in range(0, len(data), 512):
        partition = data[i:i+512]

        if len(partition) != 512:
            for index in range(512 - len(partition)):
                partition += b'\x00'

        write_sector(cluster_chain[chain_num], partition)
        chain_num += 1
    return True



def delete_file(FAT: list[int], entry: DirectoryEntry) -> bool:
    """Remove file and free its clusters."""

def find_duplicate_file(FAT: list[int], dir_cluster: int, name: str, extension: str) -> bool:
    """Find duplicate files."""
    file_entry = find_entry(FAT, name, dir_cluster)
    if file_entry is None: # entry exists
        return False
    elif file_entry.attributes & 0x10 == 0x10: # is a folder
        return False
    elif file_entry.extension != extension: # extension matches
        return False
    return True