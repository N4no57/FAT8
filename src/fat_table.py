from src.utils import TOTAL_CLUSTERS

FAT = [0 for _ in range(TOTAL_CLUSTERS)]

def is_free(cluster: int) -> bool:
    return FAT[cluster] == 0

def is_eof(cluster: int) -> bool:
    return FAT[cluster] == 0xFF