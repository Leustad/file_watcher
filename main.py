import hashlib
import logging
import os
import sys
import time
from datetime import date
from shutil import copy2, rmtree

from tqdm import tqdm

# SOURCE_DIR = 'E:\\DEEPFREEZE\\'
# TARGET_1_DIR = '\\\\LEUSTAD-DATA\\Docs\\Personal\\'
# TRASHCAN = '\\\\LEUSTAD-DATA\\Docs\\Personal\\Deleted\\'

BLOCKSIZE = 65536
SOURCE_DIR = 'E:\\Development\\Python\\file_watcher\\source\\'
TARGETS = ['E:\\Development\\Python\\file_watcher\\destination\\', 'E:\\Development\\Python\\books_api\\']
TRASHCAN = 'E:\\Development\\Python\\file_watcher\\destination\\Deleted\\'


logger = logging.getLogger('file_watcher')
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)
logging.basicConfig(filename=f'E:\\Development\\Python\\file_watcher\\logs\\file_watcher.info.{date.today()}.log',
                    filemode='a',
                    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.DEBUG)


class FileCore:
    _registery = {}

    def __init__(self, path, name):
        self._registery[name] = self
        self.name = name
        self.path = path
        self.index = self.index_files(self.path)
        # self.hash_map = 
        
    @classmethod
    def by_name(cls, name):
        return cls._registery[name]

    @staticmethod    
    def get_hash(path):
        with open(os.path.join(path), 'rb') as afile:
            buf = afile.read(BLOCKSIZE)
            hasher = hashlib.md5()
            while len(buf) > 0:
                hasher.update(buf)
                buf = afile.read(BLOCKSIZE)
        return hasher.hexdigest()

    def index_files(self, directory):
        indexed = {}
        for (dirpath, dirnames, filenames) in os.walk(directory):
            for filename in filenames:
                if 'Deleted' not in dirpath:
                    pathway = os.path.join(dirpath, filename)
                    pathway = pathway.split(directory)[1]
                    indexed[pathway] = self.get_hash(os.path.join(dirpath, filename))
        return indexed

    
source = FileCore(SOURCE_DIR, 'source')
for idx, val in enumerate(TARGETS):
	val = FileCore(val, f'target_{idx}')

for key, val in FileCore._registery.items():
    print(key, FileCore._registery[key].index)


# def get_hash(path):
#     with open(os.path.join(path), 'rb') as afile:
#         buf = afile.read(BLOCKSIZE)
#         hasher = hashlib.md5()
#         while len(buf) > 0:
#             hasher.update(buf)
#             buf = afile.read(BLOCKSIZE)
#     return hasher.hexdigest()


# def index_files(directory):
#     indexed = {}
#     for (dirpath, dirnames, filenames) in os.walk(directory):
#         for filename in filenames:
#             if 'Deleted' not in dirpath:
#                 pathway = os.path.join(dirpath, filename)
#                 pathway = pathway.split(directory)[1]
#                 indexed[pathway] = get_hash(os.path.join(dirpath, filename))
#     return indexed

# def check_hash(path, hash, targets):
#     for key, value in targets.items():
#         if value.get(path) and value[path] != hash:
#             return {key: path}


# def check_diff(targets, source):
#     for key in targets:
#         add_to[key] = (set(source.keys()) - set(targets[key].keys()))
#         deleted_from[key] = (set(targets[key].keys()) - set(source.keys()))
#     print(f'add_to: {add_to}')
#     print(f'deleted_from: {deleted_from}')
#     for path, hash in source.items():
#         value = check_hash(path, hash, targets)
#         if value:
#             changed_at.update(value)
#     print(f'changed_at: {changed_at}')


# def main():
#     for idx, path in enumerate(TARGET):
#         target_indexed[f'target_{idx}'] = index_files(path)
#     source_indexed = index_files(SOURCE_DIR)
#     print(target_indexed)
#     print(source_indexed)
#     check_diff(target_indexed, source_indexed)

# main()


# class FileWatcher():
#     def __init__(self, source, target, trash_can, logger):
#         self.source = source
#         self.target = target
#         self.trash_can = trash_can
#         self.logger = logger
#         self.source_hash_map = {}
#         self.target_hash_map = {}
#         self.ctr = 0


#     # def index_files(self, directory):
#     #     self.indexed = []
#     #     for (dirpath, dirnames, filenames) in os.walk(directory):
#     #         for filename in filenames:
#     #             self.indexed.append(os.path.join(dirpath, filename))
#     #     return self.indexed

#     @staticmethod
#     def hash_me(path, file):
#         with open(os.path.join(path, file), 'rb') as afile:
#             buf = afile.read(BLOCKSIZE)
#             hasher = hashlib.md5()
#             while len(buf) > 0:
#                 hasher.update(buf)
#                 buf = afile.read(BLOCKSIZE)
#         return hasher.hexdigest()

#     def add_files(self, added):
#         for file in added:
#             self.destination_file = os.path.join(self.target, os.path.join(file))
#             if '\\' in file:
#                 self.destinatination_dir = os.path.join(self.target, os.path.join(*file.split('\\')[:-1]))
#                 os.makedirs(self.destinatination_dir, exist_ok=True)
#             self.destinatination_dir = os.path.join(self.target, file)
#             self.source_dir = os.path.join(self.source, file)

#             copy2(self.source_dir, self.destinatination_dir)
#             self.logger.info(f'Added to: {self.destination_file}')


#     def remove_files(self, deleted):
#         self.ctr = 0
#         for file in deleted:
#             if 'Deleted' in file or 'Thumbs.db' in file:
#                 continue
#             if '\\' in file:
#                 self.destinatination_dir = os.path.join(self.trash_can, os.path.join(*file.split('\\')[:-1]))
#                 os.makedirs(self.destinatination_dir, exist_ok=True)
#             self.move_from = os.path.join(self.target, file)  
#             self.move_to = os.path.join(self.trash_can, file)
            
#             if os.path.exists(self.move_to):
#                 self.move_to = os.path.join(self.trash_can, f'{file}_#COPY#')
            
#             os.rename(self.move_from, self.move_to)
#             self.ctr += 1
#             self.logger.info(f'Deleted from: {self.move_from}')

#         return self.ctr


#     def check_empty_dir(self, directory):
#         self.files = os.listdir(directory)
#         if len(self.files):
#             for f in self.files:
#                 if f == 'Deleted':
#                     continue
#                 self.fullpath = os.path.join(directory, f)
#                 if os.path.isdir(self.fullpath):
#                     self.check_empty_dir(self.fullpath)

#         # if folder empty, delete it
#         self.files = os.listdir(directory)
#         if len(self.files) == 0:
#             self.logger.info(f'Removed emtpy dir: {directory}')
#             os.rmdir(directory)


#     def execute(self):
#         self.source_files = [i.split(self.source)[1] for i in tqdm(self.index_files(self.source))]
#         self.target_files = [i.split(self.target)[1] for i in tqdm(self.index_files(self.target))]

#         self.added = set(self.source_files).difference(set(self.target_files))
#         self.deleted = set(self.target_files).difference(set(self.source_files))

#         self.logger.info('===== Summary =====')
#         if self.added:
#             self.add_files(self.added)
#             self.logger.info(f'Added: {len(self.added)} files')

#         if self.deleted:
#             self.deleted_count = self.remove_files(self.deleted)
#             self.logger.info(f'Deleted: {self.deleted_count} files')
#             self.check_empty_dir(self.target)
        
#         self.logger.info('Cycle Completed !!')


# if __name__ == "__main__":
#     file_watcher = FileWatcher(SOURCE_DIR, TARGET_1_DIR, TRASHCAN, logger)
#     file_watcher.execute()