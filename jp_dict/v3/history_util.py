import glob
import json
import os
from tqdm import tqdm


class HistoryUtil:
    @staticmethod
    def get_history_paths(historyDir: str) -> list[str]:
        result: list[str] = []
        for path in glob.glob(f"{historyDir}/*"):
            if os.path.isfile(path):
                filename = os.path.basename(path)
                if filename in ['BrowserHistory.json', 'History.json']:
                    result.append(path)
            elif os.path.isdir(path):
                result.extend(HistoryUtil.get_history_paths(path))
            else:
                pass
        return result

    @staticmethod
    def calc_combined_history(
        historyPaths: str, showPbar: bool=False
    ) -> list[dict]:
        combinedTimeEntryMap: dict[int, dict] = dict()
        if showPbar:
            historyPaths = tqdm(historyPaths, desc='Combining Histories', leave=True)
        for path in historyPaths:
            data = json.load(open(path, 'r'))
            entries: list[dict] = data['Browser History'][::-1]
            if not showPbar:
                while len(entries) > 0:
                    entry = entries.pop()
                    combinedTimeEntryMap[entry['time_usec']] = entry
            else:
                pbar = tqdm(total=len(entries), leave=False)
                while len(entries) > 0:
                    entry = entries.pop()
                    combinedTimeEntryMap[entry['time_usec']] = entry
                    pbar.update()
                pbar.close()
        combinedEntries: list[dict] = list(combinedTimeEntryMap.values())
        combinedEntries.sort(key=lambda obj: obj['time_usec'])
        return combinedEntries
