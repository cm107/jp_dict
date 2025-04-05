from __future__ import annotations
import glob
import json
import os
import shutil
from .log import LogModule
from .meta_module import MetaDirectoryModule
from .history import HistoryModule

class ExampleModule(MetaDirectoryModule):
    def __init__(self, meta: MetaDirectory):
        super().__init__(meta)
        self.name = 'example'

    def convert_to_dict(self, item_dict: dict):
        pass

    @classmethod
    def extract_prepostinit(cls, item_dict: dict) -> tuple[dict, dict]:
        return {}, item_dict

class MetaDirectory:
    def __init__(self, metaDir: str):
        self.metaDir = metaDir
        self.configPath = f"{metaDir}/config.json"
        self.dataDir = f"{metaDir}/data"
        self.combinedHistoryPath = f"{self.dataDir}/combinedHistory.json"
        self.logDir = f"{self.metaDir}/log"

        # Modules
        self.example = ExampleModule(self)
        self.history = HistoryModule(self)
        self.log = LogModule(self)

    def save(self):
        _dict = dict(
            example=self.example.to_dict(),
            history=self.history.to_dict(),
            log=self.log.to_dict(),
        )
        json.dump(
            _dict, open(self.configPath, 'w'),
            ensure_ascii=False,
            indent=2
        )
    
    @classmethod
    def load(cls) -> MetaDirectory:
        meta = MetaUtil.find_meta_dir()
        data: dict = json.load(open(meta.configPath, 'r'))
        for key, val in data.items():
            if key == 'example':
                meta.example = ExampleModule.from_dict(meta, val)
            elif key == 'history':
                meta.history = HistoryModule.from_dict(meta, val)
            elif key == 'log':
                meta.log = LogModule.from_dict(meta, val)
            else:
                raise NotImplementedError(f"{key=}")
        return meta

    def is_initialized(self) -> bool:
        return os.path.isdir(self.metaDir)

    @staticmethod
    def clear_dir(dirPath: str):
        for path in glob.glob(f"{dirPath}/*"):
            if os.path.isfile(path):
                os.remove(path)
            elif os.path.isdir(path):
                shutil.rmtree(path)
            else:
                raise NotImplementedError
    
    def _init_meta_dir(self):
        for dirPath in [
            self.metaDir,
            self.dataDir,
            self.logDir,
        ]:
            os.makedirs(dirPath, exist_ok=False)
        self.save()

    def init_meta_dir(self):
        if self.is_initialized():
            msg = f"Meta directory already exists at {self.metaDir}."
            msg += "\nWould you like to clear it? (y/n) "
            if input(msg).lower() in ['y', 'yes']:
                MetaDirectory.clear_dir(self.metaDir)
                self._init_meta_dir()
            else:
                return
        else:
            self._init_meta_dir()

class MetaUtil:
    @staticmethod
    def get_global_meta_dir() -> str:
        homeDir = os.path.expanduser('~')
        return f"{homeDir}/.jpdict"

    @staticmethod
    def get_local_meta_dir() -> str:
        cwd = os.getcwd()
        return f"{cwd}/.jpdict"

    @staticmethod
    def find_meta_dir() -> MetaDirectory | None:
        globalMetaDir = MetaUtil.get_global_meta_dir()
        localMetaDir = MetaUtil.get_local_meta_dir()
        if os.path.isdir(localMetaDir):
            return MetaDirectory(localMetaDir)
        elif os.path.isdir(globalMetaDir):
            return MetaDirectory(globalMetaDir)
        else:
            return None
    
    @staticmethod
    def init_meta_dir(globalFlag: bool=False):
        metaDirPath = MetaUtil.get_global_meta_dir() \
            if globalFlag else MetaUtil.get_local_meta_dir()
        metaDir = MetaDirectory(metaDirPath)        
        metaDir.init_meta_dir()
