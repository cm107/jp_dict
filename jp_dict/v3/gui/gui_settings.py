from dataclasses import dataclass
import os
from .meta_util import MetaUtil

@dataclass
class GuiSettings:
    windowTitle = "JP Dict"
    windowSize = (1280, 720)
    windowPos = (100, 100)
    historyDir = "/home/clayton/workspace/data/study/jp_dict_data/browser_history"
    fontSize = 20
    invalidSearchStrList = [
        '#kanji', '#sentences', '#names', '*', '?',
        '＊', '？', '#', '＃'
    ]
    metaDirName = '.jp_dict'
    metaDirIsLocal = False

    @property
    def metaDirPath(self):
        return MetaUtil.get_meta_dir(
            self.metaDirName, localFlag=self.metaDirIsLocal
        )

    @property
    def jishoDataDir(self) -> str:
        dirPath = f"{self.metaDirPath}/jisho_data"
        os.makedirs(dirPath, exist_ok=True)
        return dirPath

guiSettings = GuiSettings()
