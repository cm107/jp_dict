import os
import glob
from tqdm import tqdm
import multiprocessing as mp
from jp_dict.parsing.myouji import MyoujiRankingParser, RankInfo, NameInfo, MyoujiResult

keepTopNames = 2000

parseDataDir = '/home/clayton/workspace/prj/data_keep/data/study/parse_data'
parseMyoujiDir = f"{parseDataDir}/myouji"
os.makedirs(parseMyoujiDir, exist_ok=True)
existingResultPaths = glob.glob(f"{parseMyoujiDir}/*.json")
if len(existingResultPaths) < keepTopNames:
    rankInfoList = MyoujiRankingParser.parse_top_names(keepTopNames, num_workers=10)
    names = [rankInfo.name for rankInfo in rankInfoList]
    assert len(names) == len(list(set(names))), f"Names are not unique."
    urls = [rankInfo.name_url for rankInfo in rankInfoList]
    urls = tqdm(urls, desc='Parsing info', unit='url(s)', leave=True)
    pool = mp.Pool(mp.cpu_count() - 2)
    nameInfoList = pool.starmap(
        MyoujiRankingParser.parse_myouji,
        zip(urls)
    )
    pool.close()
    results: list[MyoujiResult] = [
        MyoujiResult(rankInfo, nameInfo)
        for rankInfo, nameInfo in zip(rankInfoList, nameInfoList)
    ]
    for result in tqdm(results, desc="Saving Parsed Myouji Results"):
        savePath = f"{parseMyoujiDir}/{result.rankInfo.name}.json"
        if not os.path.isfile(savePath):
            result.save(savePath)
else:
    results: list[MyoujiResult] = []
    for path in existingResultPaths:
        results.append(MyoujiResult.load(path))

counter: dict[str, int] = {}
for result in results:
    for char in result.rankInfo.name:
        if char in counter:
            counter[char]['count'] += 1
            if counter[char]['highestRank'].rank > result.rankInfo.rank:
                counter[char]['highestRank'] = result.rankInfo
            if result.rankInfo.name not in counter[char]['names']:
                counter[char]['names'].append(result.rankInfo.name)
        else:
            counter[char] = {'count': 1, 'highestRank': result.rankInfo, 'names': [result.rankInfo.name]}
kanjiCounts: list[tuple[str, dict]] = list(counter.items())
kanjiCounts.sort(key=lambda x: x[1]['highestRank'].rank, reverse=False)

learned_kanji_txt_path = f'/home/clayton/workspace/prj/data_keep/data/study/anki/kanji/learned_kanji_combined.txt'
f = open(learned_kanji_txt_path, 'r')
lines = f.readlines()
learned_kanji_list = [line.replace('\n', '') for line in lines]
f.close()
koohiiParseDump = f"{parseDataDir}/koohii_parse_dump"
koohiiLearnedKanji = [
    os.path.splitext(os.path.basename(path))[0]
    for path in glob.glob(f"{koohiiParseDump}/*.json")
]
for kanji in koohiiLearnedKanji:
    if kanji not in learned_kanji_list:
        learned_kanji_list.append(kanji)

for idx, (kanji, dataDict) in enumerate(kanjiCounts):
    if kanji in learned_kanji_list:
        continue
    count = dataDict['count']
    highestRank: RankInfo = dataDict['highestRank']
    names: list[str] = dataDict['names']
    print(f"{idx=}: {kanji=}, {highestRank.rank}, {count=}")
    for nameIdx, name in enumerate(names):
        print(f"\t{nameIdx}: {name}")