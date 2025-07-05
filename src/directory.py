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
        if self.attributes != 0x10:
            return f"<DirectoryEntry '{self.filename}.{self.extension}' size={self.file_size} cluster={self.first_cluster}>"
        else:
            return f"<DirectoryEntry '{self.filename}' cluster={self.first_cluster}>"

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
    return entry

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
    return entry
