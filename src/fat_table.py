from src.utils import TOTAL_CLUSTERS

FAT = [0 for _ in range(TOTAL_CLUSTERS)]

def allocate_cluster_chain(count: int) -> list:
    """Allocate a chain of `count` clusters and return their indices in order."""

def free_cluster_chain(start_cluster: int) -> None:
    """Free all clusters in the chain starting at `start_cluster`."""

def get_cluster_chain(start_cluster: int) -> list[int]:
    """Return all clusters in the chain starting at `start_cluster`."""

def is_free(cluster: int) -> bool:
    return FAT[cluster] == 0

def is_eof(cluster: int) -> bool:
    return FAT[cluster] == 0xFF