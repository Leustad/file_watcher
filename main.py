import logging
import os
import sys
import time
from datetime import date
from shutil import copy2, rmtree

from tqdm import tqdm

SOURCE_DIR = 'E:\\DEEPFREEZE\\'
TARGET_1_DIR = '\\\\LEUSTAD-DATA\\Docs\\Personal\\'
TRASHCAN = '\\\\LEUSTAD-DATA\\Docs\\Personal\\Deleted\\'

logger = logging.getLogger('file_watcher')
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)
logging.basicConfig(filename=f'E:\\Development\\Python\\file_watcher\\logs\\file_watcher.info.{date.today()}.log',
                    filemode='a',
                    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.DEBUG)



def index_files(directory):
    indexed = []
    for (dirpath, dirnames, filenames) in os.walk(directory):
        for filename in filenames:
            indexed.append(os.path.join(dirpath, filename))
    return indexed


def check_empty_dir(directory):
    for (dirpath, dirnames, filenames) in os.walk(directory):
        if len(dirnames) == 0 and len(filenames) == 0 and 'Deleted' not in dirpath:
            rmtree(dirpath)
            logger.info(f'Removed emtpy dir: {dirpath}')


def add_files(added):
    for file in added:
        destination_file = os.path.join(TARGET_1_DIR, os.path.join(file))
        if '\\' in file:
            destinatination_dir = os.path.join(TARGET_1_DIR, os.path.join(*file.split('\\')[:-1]))
            os.makedirs(destinatination_dir, exist_ok=True)
        destinatination_dir = os.path.join(TARGET_1_DIR, file)
        source_dir = os.path.join(SOURCE_DIR, file)

        copy2(source_dir, destinatination_dir)
        logger.info(f'Added to: {destination_file}')


def remove_files(deleted):
    for file in deleted:
        if 'Deleted' in file:
            continue
        if '\\' in file:
            destinatination_dir = os.path.join(TRASHCAN, os.path.join(*file.split('\\')[:-1]))
            os.makedirs(destinatination_dir, exist_ok=True)
        move_from = os.path.join(TARGET_1_DIR, file)  
        move_to = os.path.join(TRASHCAN, file)
        
        if os.path.exists(move_to):
            move_to = os.path.join(TRASHCAN, f'{file}_#COPY#')
        
        os.rename(move_from, move_to)
        logger.info(f'Deleted from: {move_from}')


def main():
    source_files = [i.split(SOURCE_DIR)[1] for i in tqdm(index_files(SOURCE_DIR))]
    target_files = [i.split(TARGET_1_DIR)[1] for i in tqdm(index_files(TARGET_1_DIR))]

    added = set(source_files).difference(set(target_files))
    deleted = set(target_files).difference(set(source_files))

    if added:
        add_files(added)

    if deleted:
        remove_files(deleted)
        check_empty_dir(TARGET_1_DIR)

if __name__ == "__main__":
    while True:
        main()
        time.sleep(360)
