import os

class MetaUtil:
    @staticmethod
    def get_global_meta_dir(dirName: str) -> str:
        homeDir = os.path.expanduser('~')
        return f"{homeDir}/{dirName}"

    @staticmethod
    def get_local_meta_dir(dirName: str) -> str:
        cwd = os.getcwd()
        return f"{cwd}/{dirName}"

    @staticmethod
    def find_meta_dir(dirName: str) -> str | None:
        globalMetaDir = MetaUtil.get_global_meta_dir(dirName)
        localMetaDir = MetaUtil.get_local_meta_dir(dirName)
        if os.path.isdir(localMetaDir):
            return localMetaDir
        elif os.path.isdir(globalMetaDir):
            return globalMetaDir
        else:
            return None
    
    @staticmethod
    def init_meta_dir(dirName: str, localFlag: bool=False) -> str:
        metaDirPath = MetaUtil.get_global_meta_dir(dirName) \
            if not localFlag else MetaUtil.get_local_meta_dir(dirName)
        os.makedirs(metaDirPath, exist_ok=True)
        return metaDirPath

    @staticmethod
    def get_meta_dir(dirName: str, localFlag: bool=False) -> str:
        if localFlag:
            # Use local directory if specified.
            metaDir = MetaUtil.get_local_meta_dir(dirName)
            if not os.path.isdir(metaDir):
                metaDir = MetaUtil.init_meta_dir(dirName, localFlag)
        else:
            # Otherwise check if global or local directory exists already.
            # Prioritize local directory if it exists.
            metaDir = MetaUtil.find_meta_dir(dirName)
            if metaDir is None:
                metaDir = MetaUtil.init_meta_dir(dirName, localFlag)
        return metaDir
