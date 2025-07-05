# FAT8 Filesystem Spec

---
## 1. Disk layout
| Region             |  Description                 | Size / Notes                       |
| ------------------ |------------------------------| ---------------------------------- |
| **Boot Sector**    | Reserved for bootloader info | 1 sector (512 bytes)               |
| **FAT Table**      | File Allocation Table        | 1 FAT, 1 byte per cluster          |
| **Root Directory** | Directory entries            | Fixed number of entries (e.g., 64) |
| **Data Region**    | Clusters for file content    | Rest of the disk                   |

---
## 2. Parameters
* __Sector size:__ 512 bytes (standard)
* __Cluster size:__ 1 sector = 512 bytes (can increase later)
* __FAT entries:__ 1 byte each (8 bits)
* __Number of clusters:__ limited by disk size — e.g., 256 clusters (1 byte indexes 0-255)
* __Special FAT Entries:__
    * `0x00` = free cluster
    * `0xFF` = End Of File (EOF)
    * Other values (1)
---
## 3. Boot Sector (512 Bytes/1 sector)
* Located at sector 0
* Reserved for bootloader code (not interpreted by FAT8)

---
## 4. FAT Table
* Begins at sector 1
* Contains one byte per cluster (256 bytes total)
* Each entry maps a cluster to the next in the chain or marks EOF

---
## 5. Root directory
* Located at sector 2
* Fixed size of 64 entries × 32 bytes = 2048 bytes
* Occupies 4 sectors (sector 2 to 5 inclusive)

---
## 6. Directory Entry Format (32 bytes)
| Offset | Size (bytes) | Description                                    |
| ------ | ------------ | ---------------------------------------------- |
| 0-7    | 8            | Filename (ASCII, padded with spaces)           |
| 8-10   | 3            | Extension (ASCII, padded with spaces)          |
| 11     | 1            | Attributes (bit flags, e.g., 0x10 = directory) |
| 12-25  | 14           | Reserved / unused                              |
| 26-27  | 2            | First cluster (little-endian)                  |
| 28-31  | 4            | File size in bytes (little-endian)             |

---
## 7. Data region
* Begins at sector 6
* Each cluster corresponds to 1 sector (512 bytes)
* File and directory contents are stored here
* Cluster chains are followed via the FAT table

---
## 8. File Allocation
* Files and directories are stored as linked cluster chains
* Starting cluster is defined in the directory entry
* FAT table maps each cluster to its successor or EOF
* Allocation occurs by scanning for free (0x00) entries

---
## 9. Special Entries in Directories
* . (dot): Refers to the current directory
* .. (dot-dot): Refers to the parent directory
* These are normal directory entries with attribute 0x10 and appropriate first_cluster values

---
# Summary
| Region         | Location         | Size                                            |
| -------------- | ---------------- | ----------------------------------------------- |
| Boot Sector    | sector 0         | 1 sector (512 bytes)                            |
| FAT Table      | sector 1         | 256 bytes (1 byte per cluster)                  |
| Root Directory | sectors 2 to 5   | 64 entries \* 32 bytes = 2048 bytes (4 sectors) |
| Data Region    | sector 6 onwards | Clusters for files/directories                  |
