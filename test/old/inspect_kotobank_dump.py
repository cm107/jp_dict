from logger import logger
from src.refactored.kotobank.kotobank_structs import KotobankResultList

results = KotobankResultList.load_from_dir('kotobank_dump')

for result in results:
    logger.yellow(result.search_word)
    logger.cyan(result.main_title)
    logger.cyan(result.main_alias_name)
    if result.main_area is None:
        continue
    for article in result.main_area.articles:
        logger.white(article.dictionary_name)
        if article.content is None:
            continue
        logger.purple(article.content.preview_str())