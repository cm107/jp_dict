from logger import logger
from src.refactored.jisho_structs import JishoSearchQueryHandler

load_path = 'queries/日_query.json'

query_handler = JishoSearchQueryHandler.load_from_path(load_path)
logger.purple(query_handler.simple_str)
# for query in query_handler:
    # logger.purple(query.url)
    # matches = query.exact_matches + query.nonexact_matches
    # for match in matches:
    #     logger.cyan(match.word_representation.simple_repr)
    #     logger.white(match.meaning_section)