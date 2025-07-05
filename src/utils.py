from random import randint

BOOT_SECTOR = 0
SECTOR_SIZE = 512
TOTAL_SECTORS = 256

CLUSTER_SIZE = 1
TOTAL_CLUSTERS = TOTAL_SECTORS // CLUSTER_SIZE

"""
=== pointers ===
"""

RESERVED_SECTOR = 0
FAT_SECTOR = 1
ROOT_DIRECTORY_SECTOR_START = 2
ROOT_DIRECTORY_SECTOR_END = 5
DATA_SECTOR_START = 6

DIRECTORY_ENTRY_SIZE = 32

IMAGE_PATH = "disk.img"

def generate_img_file():
    with open("disk.img", "wb+") as f:
        for i in range(TOTAL_SECTORS * SECTOR_SIZE):
            f.write(randint(0, 255).to_bytes(1, byteorder='little'))

        f.seek(0)
        for i in range(ROOT_DIRECTORY_SECTOR_END * SECTOR_SIZE):
            f.write(int(0).to_bytes(1, byteorder='little'))
