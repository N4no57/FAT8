from utils import SECTOR_SIZE, IMAGE_PATH

def read_sector(sector_number: int) ->bytes:
    with open(IMAGE_PATH, 'rb') as image:
        image.seek(sector_number*SECTOR_SIZE)
        return image.read(SECTOR_SIZE)

def write_sector(sector_number: int, data: bytes) -> None:
    if len(data) != SECTOR_SIZE:
        raise ValueError('Data must be of size {}'.format(SECTOR_SIZE))
    with open(IMAGE_PATH, 'r+b') as image:
        image.seek(sector_number*SECTOR_SIZE)
        image.write(data)