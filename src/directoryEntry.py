from src.utils import DIRECTORY_ENTRY_SIZE


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

    def __repr__(self):
        return f"<DirectoryEntry '{self.filename}.{self.extension}' size={self.file_size} cluster={self.first_cluster}>"