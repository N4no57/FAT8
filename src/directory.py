import math

from setuptools.command.egg_info import write_entries

from src.disk import read_sector, write_sector
from src.fat_table import allocate_cluster_chain, get_cluster_chain, free_cluster_chain
from src.utils import DIRECTORY_ENTRY_SIZE, TOTAL_CLUSTERS, DATA_SECTOR_START, SECTOR_SIZE, ROOT_DIRECTORY_SECTOR_START


class DirectoryEntry:
    def __init__(self, data):
        if len(data) != DIRECTORY_ENTRY_SIZE:
            raise ValueError("invalid entry size\nEntry data must be 32 byte long")
        self.data = data

    @property
    def filename(self):
        # bytes 0-7: filename padded with spaces (ASCII)
        return bytes(self.data[0:8]).decode('ascii').rstrip()

    @property
    def extension(self):
        # bytes 8-10: file extension padded with spaces
        return bytes(self.data[8:11]).decode('ascii').rstrip()

    @property
    def attributes(self):
        # byte 11: attribute flags
        return self.data[11]

    @property
    def first_cluster(self):
        # bytes 26-27: little endian starting cluster number
        low = self.data[26]
        high = self.data[27]
        return (high << 8) | low

    @property
    def file_size(self):
        # bytes 28-31: little endian file size (4 bytes)
        return self.data[28] + (self.data[29] << 8) + (self.data[30] << 16) + (self.data[31] << 24)

    def pack(self):
        byte_data = b''
        for i in range(DIRECTORY_ENTRY_SIZE):
            byte_data += self.data[i].to_bytes(1, 'little')
        return byte_data

    def unpack(self, data: bytes):
        if len(data) != DIRECTORY_ENTRY_SIZE:
            raise ValueError("invalid entry size\nEntry data must be 32 byte long")
        self.data = int.from_bytes(data, 'little')

    def __repr__(self):
        if self.attributes != 0x10:
            return f"<DirectoryEntry '{self.filename}.{self.extension}' size={self.file_size} cluster={self.first_cluster}>"
        else:
            return f"<DirectoryEntry '{self.filename}' cluster={self.first_cluster}>"

def read_directory(FAT: list[int], cluster: int) -> list[DirectoryEntry]:
    """Reads a directory starting at a given cluster. following FAT chains if the directory spans multiple clusters.
    Returns a list of DirectoryEntry objects"""
    directory_entries = []

    for cluster in get_cluster_chain(FAT, cluster):
        data = read_sector(cluster)
        for i in range(0, len(data), DIRECTORY_ENTRY_SIZE):
            entry_data = data[i:i + DIRECTORY_ENTRY_SIZE]
            if all(b == 0x00 for b in entry_data):
                continue  # skip empty slots
            directory_entries.append(DirectoryEntry(entry_data))

    return directory_entries

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

def delete_directory(FAT: list[int], name: str, cwd: int):
    delete_entry(FAT, name, cluster)

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
