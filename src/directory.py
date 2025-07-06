import math
from src.disk import  write_sector
from src.fat_table import allocate_cluster_chain, get_cluster_chain, free_cluster_chain
from src.fs import DirectoryEntry, read_directory
from src.utils import DIRECTORY_ENTRY_SIZE, TOTAL_CLUSTERS, SECTOR_SIZE, ROOT_DIRECTORY_SECTOR_START

def write_directory(FAT: list[int], cluster: int, entries: list[DirectoryEntry]) -> None:
    """Writes a list of DirectoryEntrys into the specified directory cluster(s).
    May require allocating new clusters if the list grows."""
    if cluster == ROOT_DIRECTORY_SECTOR_START:
        if len(entries) > 80:
            print("no more room in root directory")
            return

    raw_data = b''.join(entry.pack() for entry in entries)
    clusters_needed = math.ceil(len(entries) / TOTAL_CLUSTERS)
    clusters = get_cluster_chain(FAT, cluster)

    if len(raw_data) < clusters[len(clusters)-1] * SECTOR_SIZE: # pad raw_data with 0x00
        for i in range(len(raw_data), clusters[len(clusters)-1] * SECTOR_SIZE):
            raw_data += b'\x00'

    if len(clusters) < clusters_needed: # TODO extend cluster chain if not root directory
        print("no more clusters directory, sucks to be you")
        return

    i = 0
    for cluster in clusters:
        write_sector(cluster, raw_data[i * SECTOR_SIZE:(i + 1) * SECTOR_SIZE])
        i += 1

def find_entry(FAT: list[int], name: str, cluster: int) -> DirectoryEntry | None:
    """Searches for an entry in the directory (useful for path resolution)"""
    directory_entries = read_directory(FAT, cluster)
    for entry in directory_entries:
        if entry.filename.strip() == name:
            return entry

def find_entry_by_cluster(FAT: list[int], target_cluster: int, start_cluster: int) -> DirectoryEntry | None:
    directory_entries = read_directory(FAT, start_cluster)
    for entry in directory_entries:
        if entry.first_cluster == target_cluster:
            return entry

def create_entry(FAT: list[int], name: str,
                 extension: str = "", is_dir: bool = False,
                 parent_cluster: int = 2, size: int = 0) -> DirectoryEntry:
    """Adds a file or subdirectory entry to a directory.
    Allocates a cluster and returns the new entry"""
    data = []
    if len(name) > 8:
        print("file name too long")
    for i in range(8):
        if i > len(name)-1:
            data.append(0x20)
            continue
        data.append(ord(name[i]))
    if len(extension) > 3:
        print("extension too long")
    for i in range(3):
        if i > len(extension) - 1:
            data.append(0x20)
            continue
        data.append(ord(extension[i]))
    if is_dir:
        data.append(0x10)
    else:
        data.append(0)
    for i in range(14):
        data.append(0)
    cluster_chain = allocate_cluster_chain(FAT, 1 if is_dir else size)
    data.append(cluster_chain[0] & 0xFF)
    data.append((cluster_chain[0] >> 8) & 0xFF)
    data.append(size & 0xFF)
    data.append((size >> 8) & 0xFF)
    data.append((size >> 16) & 0xFF)
    data.append((size >> 24) & 0xFF)

    parent_entries = read_directory(FAT, parent_cluster)
    parent_entries.append(DirectoryEntry(data))

    write_directory(FAT, parent_cluster, parent_entries)

    return DirectoryEntry(data)

def delete_entry(FAT: list[int], name: str, cluster: int):
    """Marks a directory entry as deleted by zeroing out the entry
    Handles cleanup if needed (e.g., freeing clusters)"""
    directory_entries = read_directory(FAT, cluster)
    located_entry = DirectoryEntry([0 for _ in range(DIRECTORY_ENTRY_SIZE)])
    for entry in directory_entries:
        if entry.filename.strip() == name:
            located_entry = entry
            break
    free_cluster_chain(FAT, located_entry.first_cluster)
    located_entry.data = [0 for _ in range(DIRECTORY_ENTRY_SIZE)]

    write_directory(FAT, cluster, directory_entries)

def list_directory(FAT: list[int], cluster: int) -> list[str]:
    """Lists filenames in a directory. Could filter out deleted entries, special system files, etc."""
    directory_entries = read_directory(FAT, cluster)
    for entry in directory_entries:
        print(entry.filename)

def create_directory(FAT: list[int], name: str, parent_cluster: int):
    directoryEntry = create_entry(FAT, name, is_dir=True, parent_cluster=parent_cluster)
    SWD = directoryEntry.first_cluster # the subdirectories Current Working Directory

    dot_entry = create_dot_entry(SWD)
    dotdot_entry = create_dotdot_entry(parent_cluster)
    subdirEntryTable = [dot_entry, dotdot_entry]
    write_directory(FAT, SWD, subdirEntryTable)

def delete_directory(FAT: list[int], name: str, cwd: str):
    delete_entry(FAT, name, 1)

##################################################
### HELPER FUNCTIONS
###################################################

def create_dot_entry(cluster):
    entry = [0] * 32
    # Filename '.' padded to 8 bytes with spaces
    entry[0] = ord('.')
    for i in range(1, 11):
        entry[i] = 0x20
    entry[11] = 0x10 # directory attribute
    entry[26] = cluster & 0xFF
    entry[27] = (cluster >> 8) & 0xFF
    return DirectoryEntry(entry)

def create_dotdot_entry(parent_cluster):
    entry = [0] * 32
    # Filename '..' padded to 8 bytes with spaces
    entry[0] = ord('.')
    entry[1] = ord('.')
    for i in range(2, 11):
        entry[i] = 0x20
    entry[11] = 0x10
    entry[26] = parent_cluster & 0xFF
    entry[27] = (parent_cluster >> 8) & 0xFF
    return DirectoryEntry(entry)
