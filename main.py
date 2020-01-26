import hashlib
import logging
import os
import sys
import time
from datetime import date
from shutil import copy2

from tqdm import tqdm

SOURCE_DIR = 'E:\\DEEPFREEZE\\'
TARGETS = ['\\\\LEUSTAD-DATA\\Docs\\Personal\\']
BLOCKSIZE = 65536

logger = logging.getLogger('file_watcher')
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)
logging.basicConfig(filename=f'E:\\Development\\Python\\file_watcher\\logs\\file_watcher.info.{date.today()}.log',
                    filemode='a',
                    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.DEBUG)

start_time = time.time()


class FileCore:
    _registry = {}

    def __init__(self, path, name):
        self._registry[name] = self
        self.name = name
        self.path = path
        self.index = self.index_files(self.path)
        
    @classmethod
    def by_name(cls, name):
        return cls._registry[name]

    @classmethod
    def instance_keys(cls):
        return cls._registry.keys()

    @staticmethod    
    def _get_hash(path):
        with open(os.path.join(path), 'rb') as afile:
            buf = afile.read(BLOCKSIZE)
            hasher = hashlib.md5()
            while len(buf) > 0:
                hasher.update(buf)
                buf = afile.read(BLOCKSIZE)
        return hasher.hexdigest()

    def index_files(self, directory):
        indexed = {}
        for (dirpath, dirnames, filenames) in tqdm(os.walk(directory),  ascii=True, desc=f'os walk {directory}'):
            for filename in filenames:
                if 'Deleted' not in dirpath:
                    pathway = os.path.join(dirpath, filename)
                    pathway = pathway.split(directory)[1]
                    indexed[pathway] = self._get_hash(os.path.join(dirpath, filename))
        return indexed


def init_objs():
    """Initialize the path objects"""
    FileCore(SOURCE_DIR, 'source')
    for idx, val in enumerate(TARGETS):
        FileCore(val, f'target_{idx}')

    val = time.time() - start_time
    logger.info(f'Finished Initializing {val:.2f} seconds')


def copy_to_target(target, source, file_path, delete_source=False):
    target_path = target
    source_dir = os.path.join(source, file_path)
    if not delete_source:
        target_path = TARGETS[int(target.split('_')[1])]
    target_dir = os.path.join(target_path, file_path)

    if '\\' in file_path:
        # Get target_dir without the file name
        target_dir = os.path.join(target_path, os.path.join(*file_path.split('\\')[:-1]))
        # Create the path if doesn't exist
        os.makedirs(target_dir, exist_ok=True)
        # Add the filename to the target_dir
        target_dir = os.path.join(target_dir, *file_path.split('\\')[-1:])

    if delete_source:
        os.rename(source_dir, target_dir)
        logger.info(f"Removed {source_dir}")
    else:
        copy2(source_dir, target_dir)
        logger.info(f'Transferred {source_dir} to {target_dir}')


def delete_empty_dir(directory):
    files = os.listdir(directory)
    if len(files):
        for f in files:
            if f == 'Deleted':
                continue
            fullpath = os.path.join(directory, f)
            if os.path.isdir(fullpath):
                delete_empty_dir(fullpath)

    # if folder empty, delete it
    files = os.listdir(directory)
    if len(files) == 0:
        logger.info(f'Removed emtpy dir: {directory}')
        os.rmdir(directory)


def compare_resources():
    source = FileCore.by_name('source')
    target_names = [i for i in FileCore.instance_keys() if i != 'source']

    for target in target_names:
        trashcan = os.path.join(FileCore.by_name(target).path, 'Deleted')

        # Compare source -> targets
        for path, hash_value in tqdm(source.index.items(), ascii=True, desc='Source -> Target'):
            if 'Thumbs.db' in path:
                continue
            # Check if the file exist at the target
            if not FileCore.by_name(target).index.get(path):
                copy_to_target(target, SOURCE_DIR, path)

            # If file exists, check the hash
            elif not FileCore.by_name(target).index[path] == hash_value:
                logger.info(f'Hash mismatch: {path} source: {hash_value} copy: {FileCore.by_name(target).index[path]}')
                copy_to_target(target, SOURCE_DIR, path)

        # Compare Targets -> Source to detect deleted files
        for path in tqdm(FileCore.by_name(target).index.keys(), ascii=True, desc='Target -> Source'):
            if 'Thumbs.db' in path:
                continue
            if not source.index.get(path):
                # Remove the file from the @target to 'Deleted' folder at the target
                copy_to_target(target=trashcan,
                               source=FileCore.by_name(target).path,
                               file_path=path,
                               delete_source=True)

        delete_empty_dir(FileCore.by_name(target).path)


if __name__ == '__main__':
    init_objs()
    compare_resources()
    val = time.time() - start_time
    logger.info(f'Execution time {val:.2f} seconds')
