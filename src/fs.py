from src.utils import DIRECTORY_ENTRY_SIZE
from src.fat_table import get_cluster_chain
from src.disk import read_sector

class DirectoryEntry:
    def __init__(self, data=None):
        if data is None:
            data = [0 for _ in range(DIRECTORY_ENTRY_SIZE)]
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
        self.data = list(data)
        return self

    def is_directory(self) -> bool:
        attribute_byte = format(self.attributes, '08b')
        return attribute_byte[3] == "1"

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
            entry = DirectoryEntry()
            entry_data = data[i:i + DIRECTORY_ENTRY_SIZE]
            if all(b == 0x00 for b in entry_data):
                continue  # skip empty slots
            directory_entries.append(entry.unpack(entry_data))

    return directory_entries