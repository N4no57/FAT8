from src.disk import write_sector, read_sector
from src.utils import SECTOR_SIZE, FAT_SECTOR, TOTAL_CLUSTERS


def allocate_cluster_chain(FAT: list[int], count: int) -> list | None:
    """Allocate a chain of `count` clusters and return their indices in order."""
    cluster_chain = []
    fat_index = 0
    while count > 0 and fat_index < len(FAT):
        if FAT[fat_index] == 0x00:
            cluster_chain.append(fat_index)
            count -= 1
        fat_index += 1

    if count > 0:
        return None # Not enough memory

    for i in range(len(cluster_chain) - 1):
        FAT[cluster_chain[i]] = cluster_chain[i + 1]

    FAT[cluster_chain[-1]] = 0xFF  # EOF

    save_FAT(FAT)

    return cluster_chain

def free_cluster_chain(FAT: list[int], start_cluster: int) -> None:
    """Free all clusters in the chain starting at `start_cluster`."""
    current = start_cluster
    while current != 0xFF and current < len(FAT):
        next_cluster = FAT[current]
        FAT[current] = 0
        if next_cluster == 0xFF:
            break
        current = next_cluster

    save_FAT(FAT)

def get_cluster_chain(FAT: list[int], start_cluster: int) -> list[int]:
    """Return all clusters in the chain starting at `start_cluster`."""
    cluster_chain = []
    current = start_cluster
    while current != 0xFF and current < len(FAT):
        cluster_chain.append(current)
        current = FAT[current]
    return cluster_chain

def save_FAT(FAT: list[int]) -> None:
    sector_data = b''

    for i in range(len(FAT)):
        sector_data += FAT[i].to_bytes(1, 'little')

    for i in range(SECTOR_SIZE - len(FAT)):
        sector_data += b'\00'

    write_sector(FAT_SECTOR, sector_data)

def load_FAT() -> list[int]:
    sector_data = []

    sector_bytes = read_sector(FAT_SECTOR)

    for i in range(TOTAL_CLUSTERS):
        sector_data.append(int(sector_bytes[i]))

    return sector_data

def is_free(FAT: list[int], cluster: int) -> bool:
    return FAT[cluster] == 0

def is_eof(FAT: list[int], cluster: int) -> bool:
    return FAT[cluster] == 0xFF