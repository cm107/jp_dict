from .jap_vocab import JapaneseVocab
from .concept import ConceptLabels
from .vocab_entry import VocabularyEntry
from ..util.previews import yellow_text, blue_text, green_text, std_text
from ..submodules.logger.logger_handler import logger

class WordResult:
    def __init__(self, jap_vocab: JapaneseVocab, concept_labels: ConceptLabels, vocab_entry: VocabularyEntry):
        self.jap_vocab = jap_vocab
        self.concept_labels = concept_labels
        self.vocab_entry = vocab_entry

    def __str__(self):
        if self.concept_labels is not None:
            return "{}\n{}\n{}".format(self.jap_vocab, self.concept_labels, self.vocab_entry)
        else:
            return "{}\n{}".format(self.jap_vocab, self.vocab_entry)

    def __repr__(self):
        return self.__str__()

class WordResultHandler:
    def __init__(self):
        self.num_results = None
        self.exact_word_results = []
        self.other_word_results = []
        self.matching_results = []

        self.display_queue = []
        self.display_count = 0

    def __str__(self):
        print_str = yellow_text + '{} result(s)'.format(self.num_results) + std_text + '\n'
        print_str += blue_text + 'Exact Results:' + std_text + '\n'
        count = 0
        for word_result in self.exact_word_results:
            count += 1
            print_str += yellow_text + '========================result {}======================='.format(count) + std_text + '\n'
            print_str += green_text + '{}'.format(word_result) + std_text
        print_str += blue_text + 'Other Results:' + std_text + '\n'
        for word_result in self.other_word_results:
            count += 1
            print_str += yellow_text + '========================result {}======================='.format(count) + std_text + '\n'
            print_str += green_text + '{}'.format(word_result) + std_text
        return print_str

    def __repr__(self):
        return self.__str__()

    def specify_num_results(self, num_results: int):
        self.num_results = num_results

    def add(self, word_result: WordResult, category: str):
        if category == 'exact_matches':
            self.exact_word_results.append(word_result)
            self.display_queue.append(word_result)
        elif category == 'other_matches':
            self.other_word_results.append(word_result)
            self.display_queue.append(word_result)
        else:
            raise Exception('Invalid category.')

    def print_display_queue(self):
        if self.display_count == 0:
            logger.yellow(f'results found: {self.num_results}')
        for word_result in self.display_queue:
            self.display_count += 1
            logger.yellow(f'========================result {self.display_count}=======================')
            logger.green(word_result)
        self.display_queue = []

    def find_matches(self, search_word: str, verbose: bool=False):
        matching_results = []
        for word in (self.exact_word_results + self.other_word_results):
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
        self.matching_results = matching_results

# word_result_handler = WordResultHandler()