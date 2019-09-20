from ..submodules.logger.logger_handler import logger
from ..lib.word_results import WordResultHandler

# TODO: Consider moving to WordResultHandler class method.
def find_matches(search_word: str, word_result_handler: WordResultHandler, verbose: bool=False):
    matching_results = []
    for word in (word_result_handler.exact_word_results + word_result_handler.other_word_results):
        jap_vocab = word.jap_vocab
        vocab_entry = word.vocab_entry
        if verbose:
            logger.blue(f"jap_vocab:\n{jap_vocab}")
            logger.blue(f"vocab_entry:\n{vocab_entry}")

        primary_writing = jap_vocab.writing
        primary_reading = jap_vocab.reading
        if primary_writing == search_word or primary_reading == search_word:
            if verbose:
                logger.yellow(f"Primary Writing: {primary_writing}, Primary Reading: {primary_reading}")
            matching_results.append(word)
            continue
        else:
            if verbose:
                logger.cyan(f"Primary Writing: {primary_writing}, Primary Reading: {primary_reading}")
        other_forms = vocab_entry.other_forms
        if other_forms is not None:
            for i, other_form in zip(range(len(other_forms.other_form_list)), other_forms.other_form_list):
                kanji_writing = other_form.kanji_writing
                kana_writing = other_form.kana_writing
                if kanji_writing == search_word or kana_writing == search_word:
                    if verbose:
                        logger.yellow(f"{i} - Kanji Writing: {kanji_writing}, Kana Writing: {kana_writing}")
                    matching_results.append(word)
                    continue
                else:
                    if verbose:
                        logger.cyan(f"{i} - Kanji Writing: {kanji_writing}, Kana Writing: {kana_writing}")
        else:
            if verbose:
                logger.cyan(f"No other forms found.")
    return matching_results