from __future__ import annotations
import glob
import os
import subprocess
from typing import TYPE_CHECKING

from .error import CLIError
if TYPE_CHECKING:
    from .meta import MetaDirectory
from .meta_module import MetaDirectoryModule

class LogModule(MetaDirectoryModule):
    def __init__(self, meta: MetaDirectory):
        super().__init__(meta)

    def convert_to_dict(self, item_dict: dict):
        pass

    @classmethod
    def extract_prepostinit(cls, item_dict: dict) -> tuple[dict, dict]:
        return item_dict, {}

    def get_lognames(self):
        logPaths = glob.glob(f"{self._meta.logDir}/*.log")
        logPaths.sort()
        lognames = [os.path.splitext(os.path.basename(path))[0] for path in logPaths]
        return lognames
    
    @staticmethod
    def _convert_to_int(strVal: str) -> int | None:
        try:
            intVal = int(strVal)
        except:
            intVal = None
        return intVal

    @staticmethod
    def _convert_to_slice(strVal: str | None) -> slice | int | None:
        if strVal is None:
            return None
        parts = strVal.split(':')
        parts = [(part if part != '' else None) for part in parts]
        if len(parts) > 1:
            mapInt = lambda x: int(x) if x is not None else None
            return slice(*list(map(mapInt, parts)))
        elif len(parts) == 1:
            return int(parts[0])
        else:
            raise ValueError(f"{strVal=}")

    def list_logs(self, sliceStr: str | None=None):
        lognames = self.get_lognames()
        if sliceStr is not None:
            sliceVal = self._convert_to_slice(sliceStr)
            listVals = list(enumerate(lognames))[sliceVal]
            if type(listVals) is not list:
                listVals = [listVals]
            for i, logname in listVals:
                print(f"{i}: {logname}")
        else:
            for i, logname in enumerate(lognames):
                print(f"{i}: {logname}")

    def delete_log(self, logname: str):
        lognames = self.get_lognames()
        if logname not in lognames:
            try:
                sliceVal = self._convert_to_slice(logname)
            except:
                sliceVal = None
                raise CLIError(f"Invalid logname or slice: {logname}")
            for _logname in lognames[sliceVal]:
                logPath = f"{self._meta.logDir}/{_logname}.log"
                assert os.path.isfile(logPath)
                os.remove(logPath)
                print(f"Deleted {_logname}")
        else:
            assert os.path.isfile(logname)
            logPath = f"{self._meta.logDir}/{logname}.log"
            os.remove(logPath)

    @staticmethod
    def linux_check_ide_command(command: str) -> bool:
        """Checks if the specified IDE command exists in the user's PATH.

        Args:
            command: The IDE command to check (e.g., 'code').

        Returns:
            True if the command exists, False otherwise.
        """

        try:
            subprocess.run(['which', command], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            return True
        except subprocess.CalledProcessError:
            return False


    def open_log(self, logname: str):
        import os
        import platform

        def open_with_default_editor(file_path, overrideDefault: str=None):
            """Opens the specified file with the user's default text editor.

            Args:
                file_path: The path to the file to open.
            """
            if platform.system() == 'Windows':
                os.startfile(file_path)
            elif platform.system() == 'Darwin':  # macOS
                os.system('open ' + file_path)
            elif platform.system() == 'Linux':
                if self.linux_check_ide_command('code'):
                    os.system('code ' + file_path)
                else:
                    os.system('xdg-open ' + file_path)
            else:
                raise ValueError('Unsupported operating system')

        idx = self._convert_to_int(logname)
        if idx is None:
            logPath = f"{self._meta.logDir}/{logname}.log"
        else:
            lognames = self.get_lognames()
            logname = lognames[idx]
            logPath = f"{self._meta.logDir}/{logname}.log"
        if not os.path.isfile(logPath):
            raise FileNotFoundError(f"{logPath=}")
        open_with_default_editor(logPath)
