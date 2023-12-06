from __future__ import annotations
import urllib3
from bs4 import BeautifulSoup
from bs4.element import Tag, NavigableString, PageElement
import json
from tqdm import tqdm
from abc import ABC
import math
import multiprocessing as mp

class LoadableBase(ABC):
    # def __init__(self):
    #     pass

    def to_dict(self):
        raise NotImplementedError
    
    @classmethod
    def from_dict(cls, item_dict):
        raise NotImplementedError
    
    def save(self, path: str):
        data = self.to_dict()
        json.dump(data, open(path, 'w'), ensure_ascii=False)
    
    def load(cls, path: str):
        data = json.load(open(path, 'r'))
        return cls.from_dict(data)

class RankInfo:
    def __init__(self, rank: int, name: str, name_url: str, numPeople: int):
        self.rank = rank
        self.name = name
        self.name_url = name_url
        self.numPeople = numPeople
    
    def __str__(self) -> str:
        paramStr = ','.join([f'{key}={val}' for key, val in self.__dict__.items()])
        return f'{type(self).__name__}({paramStr})'
    
    def __repr__(self) -> str:
        return self.__str__()
    
    def to_dict(self) -> dict:
        return self.__dict__
    
    @classmethod
    def from_dict(cls, item_dict: dict) -> RankInfo:
        return cls(**item_dict)
    
    @staticmethod
    def batch_to_dict(batch: list[RankInfo]) -> list[dict]:
        return [obj.to_dict() for obj in batch]
    
    @staticmethod
    def batch_from_dict(batch_dict: list[dict]) -> list[RankInfo]:
        return [RankInfo.from_dict(item_dict) for item_dict in batch_dict]
    
    @staticmethod
    def save(obj: RankInfo | list[RankInfo], path: str):
        if type(obj) is RankInfo:
            data = obj.to_dict()
        elif type(obj) is list:
            data = RankInfo.batch_to_dict(obj)
        else:
            raise TypeError
        
        json.dump(data, open(path, 'w'), ensure_ascii=False)
    
    @staticmethod
    def load(path: str) -> RankInfo | list[RankInfo]:
        data = json.load(open(path, 'r'))
        if type(data) is dict:
            return RankInfo.from_dict(data)
        elif type(data) is list:
            return RankInfo.batch_from_dict(data)
        else:
            raise TypeError

class RankInfoList(list[RankInfo], LoadableBase):
    def __init__(self, _objects: list[RankInfo]=[]):
        self._objects = _objects
        raise NotImplementedError

class NameInfo:
    def __init__(
        self,
        representationHtml: str, # Post 1
        rankingSummaryHtml: str, # Post 2
        myoujiCommentsHeadingHtml: str, # Post 3
        myoujiCommentsHtml: str,
        updateInfo: str,
        mapHtml: str,
        topFiveByRegionHtml: str, # Post 4
        topTenCelebs: str, # Post 5
        userPostedNameOriginHtml: str, # Post 7
        userPostedKamonOriginHtml: str
    ):
        # Post 1
        self.representationHtml = representationHtml

        # Post 2
        self.rankingSummaryHtml = rankingSummaryHtml
        
        # Post 3
        self.myoujiCommentsHeadingHtml = myoujiCommentsHeadingHtml
        self.myoujiCommentsHtml = myoujiCommentsHtml
        self.updateInfo = updateInfo
        self.mapHtml = mapHtml

        # Post 4
        self.topFiveByRegionHtml = topFiveByRegionHtml

        # Post 5
        self.topTenCelebs = topTenCelebs

        # Post 7
        self.userPostedNameOriginHtml = userPostedNameOriginHtml
        self.userPostedKamonOriginHtml = userPostedKamonOriginHtml
    
    def to_dict(self) -> dict:
        return self.__dict__
    
    @classmethod
    def from_dict(cls, item_dict: dict) -> NameInfo:
        return NameInfo(**item_dict)

    @staticmethod
    def batch_to_dict(batch: list[NameInfo]) -> list[dict]:
        return [obj.to_dict() for obj in batch]
    
    @staticmethod
    def batch_from_dict(batch_dict: list[dict]) -> list[NameInfo]:
        return [NameInfo.from_dict(item_dict) for item_dict in batch_dict]
    
    @staticmethod
    def save(obj: NameInfo | list[NameInfo], path: str):
        if type(obj) is NameInfo:
            data = obj.to_dict()
        elif type(obj) is list:
            data = NameInfo.batch_to_dict(obj)
        else:
            raise TypeError
        
        json.dump(data, open(path, 'w'), ensure_ascii=False)
    
    @staticmethod
    def load(path: str) -> NameInfo | list[NameInfo]:
        data = json.load(open(path, 'r'))
        if type(data) is dict:
            return NameInfo.from_dict(data)
        elif type(data) is list:
            return NameInfo.batch_from_dict(data)
        else:
            raise TypeError

    @property
    def html(self) -> str:
        def details(innerHtml: str, summary: str) -> str:
            return f'<details><summary>{summary}</summary>{innerHtml}</details>'

        result = ""
        
        result += self.representationHtml

        result += self.rankingSummaryHtml

        result += self.myoujiCommentsHeadingHtml
        result += self.myoujiCommentsHtml
        result += self.updateInfo
        result += details(self.mapHtml, "Show Name Distribution On Map")
        # result += self.mapHtml

        # result += self.topFiveByRegionHtml
        result += details(self.topFiveByRegionHtml, "Show Top Five By Region")

        # result += self.topTenCelebs
        result += details(self.topTenCelebs, "Show Top Ten Celebrities")

        # result += self.userPostedNameOriginHtml
        result += details(self.userPostedNameOriginHtml, "Show User Posted Etymology")
        # result += self.userPostedKamonOriginHtml
        result += details(self.userPostedKamonOriginHtml, "User Posted Kamon")
        return result

class MyoujiResult:
    def __init__(self, rankInfo: RankInfo, nameInfo: NameInfo):
        self.rankInfo = rankInfo
        self.nameInfo = nameInfo
    
    def to_dict(self) -> dict:
        return {
            'rankInfo': self.rankInfo.to_dict(),
            'nameInfo': self.nameInfo.to_dict()
        }
    
    @classmethod
    def from_dict(cls, item_dict: dict) -> MyoujiResult:
        return MyoujiResult(
            rankInfo=RankInfo.from_dict(item_dict['rankInfo']),
            nameInfo=NameInfo.from_dict(item_dict['nameInfo'])
        )

    def save(self, path: str):
        data = self.to_dict()
        json.dump(data, open(path, 'w'), ensure_ascii=False)
    
    @classmethod
    def load(cls, path: str) -> MyoujiResult:
        data = json.load(open(path, 'r'))
        return MyoujiResult.from_dict(data)

class MyoujiRankingParser:
    baseUrl: str = 'https://myoji-yurai.net'
    rankingBaseUrl: str = f'{baseUrl}/prefectureRanking.htm'

    def __init__(self):
        pass

    @classmethod
    def parse(cls, pref: str='全国', page: int=0) -> list[RankInfo]:
        url = f"{cls.rankingBaseUrl}?prefecture={pref}&page={page}"
        
        rankInfoList: list[RankInfo] = []
        http = urllib3.PoolManager()
        page = http.request(method='GET', url=url)
        soup = BeautifulSoup(page.data, 'html.parser')
        contentHtml: Tag = soup.find(id='content')
        tableHtmlList: list[Tag] = contentHtml.find_all(name='table', class_='simple')
        for tableHtml in tableHtmlList:
            rowHtmlList: list[Tag] = (
                tableHtml
                .find(name='tbody')
                .find_all(name='tr', class_='odd')
            )
            for rowHtml in rowHtmlList:
                cellHtmlList: list[Tag] = rowHtml.find_all(name='td')
                assert len(cellHtmlList) == 3
                rank: int = int(cellHtmlList[0].text.strip().replace('位', ''))
                name: str = cellHtmlList[1].text.strip()
                name_href = cellHtmlList[1].find(name='a')['href']
                name_url = f"{MyoujiRankingParser.baseUrl}/{name_href}"
                numPeople: int = int(
                    cellHtmlList[2].text.strip()
                    .replace('およそ', '')
                    .replace('人', '')
                    .replace(',', '')
                )
                rankInfo = RankInfo(rank=rank, name=name, name_url=name_url, numPeople=numPeople)
                rankInfoList.append(rankInfo)
        return rankInfoList

    @classmethod
    def parse_myouji(cls, url: str, debugHtml: bool=False):
        http = urllib3.PoolManager()
        page = http.request(method='GET', url=url)
        soup = BeautifulSoup(page.data, 'html.parser')
        contentHtml: Tag = soup.find(id='content')
        
        postHtmlList = contentHtml.find_all(name='div', class_='post')
        import re
        relevant_aHtml_regex = re.compile("[a-z,A-Z,0-9]*\.htm")
        for postHtml in postHtmlList:
            for aHtml in postHtml.find_all(name='a'):
                if relevant_aHtml_regex.match(aHtml['href']):
                    aHtml['href'] = f"{MyoujiRankingParser.baseUrl}/{aHtml['href']}"
            for imgHtml in postHtml.find_all(name='img'):
                if imgHtml['src'].startswith('images'):
                    imgHtml['src'] = f"{MyoujiRankingParser.baseUrl}/{imgHtml['src']}"

            for clearHtml in postHtml.find_all(class_='clear'):
                if 'style' not in clearHtml.attrs:
                    clearHtml['style'] = "clear: both;"
                elif 'clear' not in clearHtml.attrs['style']:
                    clearHtml['style'] += "clear: both;"

        # Post 1
        representationHtml = postHtmlList[0]

        # Post 2
        rankingSummaryHtml = postHtmlList[1]

        # Post 3
        boxHtml: Tag = postHtmlList[2].find(name='div', class_="box")
        myoujiCommentsHeadingHtml: Tag = boxHtml.find(name='h4')
        myoujiCommentsHtml = boxHtml.find(name='div', class_="myojiComments")
        for linkHtml in myoujiCommentsHtml.find_all(name='a'):
            if linkHtml['href'].startswith('searchResult.htm'):
                linkHtml['href'] = f"{MyoujiRankingParser.baseUrl}/{linkHtml['href']}"
        pTags = [
            tag
            for tag in boxHtml.parent.find_all(name='p')
            if tag.text.strip().startswith('最終更新')
        ]
        if len(pTags) > 0:
            updateInfo = pTags[0]
        else:
            updateInfo = None
        mapHtml = contentHtml.find(name='div', id='mapBox')
        mapBoxIframeHtml = mapHtml.find(name='iframe')
        mapBoxIframeHtml['src'] = f"{MyoujiRankingParser.baseUrl}/{mapBoxIframeHtml['src']}"
        # mapBoxIframeHtml['style'] = "min-width: 100vw; min-height: 100vh;"
        mapBoxIframeHtml['style'] = "width: 100%; height: 100%;"
        # mapBoxIframeHtml['style'] = "width: auto; height: auto;"

        # Post 4
        topFiveByRegionHtml = postHtmlList[3]

        # Post 5
        topTenCelebs = postHtmlList[4]

        # Post 6 (Skipped)

        # Post 7 (Needs cleaning)
        simpleYuraiTables = postHtmlList[6].find_all(name='table', class_="simple yuraiTable")
        # print(f"{len(simpleYuraiTables)=}")
        userPostedNameOriginHtml = simpleYuraiTables[0]
        userPostedKamonOriginHtml = simpleYuraiTables[2]

        # Post 8 ~ 10 (Skipped)

        # print(f"{len(postHtmlList)=}")

        nameInfo = NameInfo(
            str(representationHtml),
            str(rankingSummaryHtml),
            str(myoujiCommentsHeadingHtml),
            str(myoujiCommentsHtml),
            str(updateInfo),
            str(mapHtml),
            str(topFiveByRegionHtml),
            str(topTenCelebs),
            str(userPostedNameOriginHtml),
            str(userPostedKamonOriginHtml)
        )
        if debugHtml:
            debugOutput = nameInfo.html

            # innerHtml = ""
            # for postHtml in postHtmlList:
            #     innerHtml += f"<br><li>{postHtml}</li>"
            # debugOutput += '<hr>' + f"<ol>{innerHtml}</ol>"
            with open('temp.html', 'w') as f:
                f.write(debugOutput)
        # exit()
        return nameInfo

    @staticmethod
    def _parse_top_names_multiproc_func(page: int) -> tuple[int, list[RankInfo]]:
        return page, MyoujiRankingParser.parse(pref='全国', page=page)

    @classmethod
    def parse_top_names(cls, numNames: int=500, num_workers: int=1):
        numPages = math.ceil(numNames / 500)
        rankInfoList: list[RankInfo] = []
        pages = list(range(numPages))
        pages = tqdm(pages)

        if num_workers is None or num_workers == 1:
            for page in pages:
                rankInfoList.extend(MyoujiRankingParser.parse(page=page))
        else:
            num_workers = min(num_workers, mp.cpu_count() - 2)
            pool = mp.Pool(num_workers)
            pairs = pool.starmap(
                MyoujiRankingParser._parse_top_names_multiproc_func,
                zip(pages)
            )
            pool.close()
            rankInfoBuffer: dict[int, list[RankInfo]] = {}
            for page, rankInfo in pairs:
                rankInfoBuffer[page] = rankInfo

            for page in range(numPages):
                rankInfoList.extend(rankInfoBuffer[page])

        return rankInfoList

    @staticmethod
    def debug():
        import os
        savePath = 'ranking.json'
        if not os.path.isfile(savePath):
            rankInfoList = MyoujiRankingParser.parse_top_names(100000, num_workers=10)
            RankInfo.save(rankInfoList, 'dump.json')
        else:
            rankInfoList = RankInfo.load(savePath)
        
        urls = [rankInfo.name_url for rankInfo in rankInfoList][:2000]
        savePath = 'info.json'
        if not os.path.isfile(savePath):
            # for rankInfo in rankInfoList:
            #     info = MyoujiRankingParser.parse_myouji(rankInfo.name_url)
            
            urls = tqdm(urls, desc='Parsing info', unit='url(s)', leave=True)
            pool = mp.Pool(mp.cpu_count() - 2)
            infoList = pool.starmap(
                MyoujiRankingParser.parse_myouji,
                zip(urls)
            )
            pool.close()
            NameInfo.save(infoList, savePath)
        else:
            infoList = NameInfo.load(savePath)
        print(f"{len(rankInfoList)=}")
        print(f"{len(infoList)=}")

        import glob
        previewDir = 'preview'
        if os.path.isdir(previewDir):
            for _path in glob.glob(f"{previewDir}/*.html"):
                os.remove(_path)
        os.makedirs(previewDir, exist_ok=True)
        for info, rankInfo in zip(infoList, rankInfoList):
            info: NameInfo = info
            rankInfo: RankInfo = rankInfo
            savePath = f"{previewDir}/{rankInfo.name}.html"
            with open(savePath, 'w') as f:
                f.write(info.html)
        