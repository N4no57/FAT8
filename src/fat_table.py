def allocate_cluster_chain(FAT: list, count: int) -> list:
    """Allocate a chain of `count` clusters and return their indices in order."""
    cluster_chain = []
    fat_index = 0
    while count > 0:
        if FAT[fat_index] != 0x00:
            fat_index+=1
            continue

        cluster_chain.append(fat_index)
        fat_index+=1
        count-=1

    for i in range(len(cluster_chain)):
        if i == (len(cluster_chain)-1):
            FAT[cluster_chain[i]] = 0xFF
            break

        FAT[cluster_chain[i]] = cluster_chain[i+1]

    return cluster_chain

def free_cluster_chain(FAT: list,start_cluster: int) -> None:
    """Free all clusters in the chain starting at `start_cluster`."""

def get_cluster_chain(FAT: list, start_cluster: int) -> list[int]:
    """Return all clusters in the chain starting at `start_cluster`."""

def is_free(FAT: list, cluster: int) -> bool:
    return FAT[cluster] == 0

def is_eof(FAT: list, cluster: int) -> bool:
    return FAT[cluster] == 0xFF