from __future__ import annotations
from .jap_vocab import JapaneseVocab
from .concept import ConceptLabels
from .vocab_entry import VocabularyEntry
from ..base import BaseParsedObject
from logger import logger

class WordResult(BaseParsedObject):
    def __init__(self, jap_vocab: JapaneseVocab, concept_labels: ConceptLabels, vocab_entry: VocabularyEntry):
        super().__init__()
        self.jap_vocab = jap_vocab
        self.concept_labels = concept_labels
        self.vocab_entry = vocab_entry

    def __str__(self):
        if self.concept_labels is not None:
            return "{}\n{}\n{}".format(self.jap_vocab, self.concept_labels, self.vocab_entry)
        else:
            return "{}\n{}".format(self.jap_vocab, self.vocab_entry)

    @classmethod
    def buffer(self, word_result: WordResult) -> WordResult:
        return word_result

    @classmethod
    def sample(self, num_samples: int=1) -> list:
        return [
            WordResult(
                jap_vocab=jap_vocab,
                concept_labels=concept_labels,
                vocab_entry=vocab_entry
            ) for jap_vocab, concept_labels, vocab_entry in \
                zip(
                    JapaneseVocab.sample(num_samples),
                    ConceptLabels.sample(num_samples),
                    VocabularyEntry.sample(num_samples)
                )
        ]

class WordResultHandler:
    def __init__(self):
        self.num_results = 0
        self.exact_word_results = []
        self.other_word_results = []
        self.matching_results = []

        self.display_queue = []
        self.display_count = 0

    def __str__(self):
        print_str = f'{self.num_results} result(s)' + '\n'
        print_str += 'Exact Results:' + '\n'
        count = 0
        for word_result in self.exact_word_results:
            count += 1
            print_str += f'========================result {count}=======================' + '\n'
            print_str += f'{word_result}'
        print_str += 'Other Results:' + '\n'
        for word_result in self.other_word_results:
            count += 1
            print_str += f'========================result {count}=======================' + '\n'
            print_str += f'{word_result}'
        return print_str

    def __repr__(self):
        return self.__str__()

    @classmethod
    def buffer(self, word_result_handler: WordResultHandler) -> WordResultHandler:
        return word_result_handler

    def copy(self, word_result_handler: WordResultHandler):
        word_result_handler0 = WordResultHandler()
        word_result_handler0.num_results = word_result_handler.num_results
        word_result_handler0.exact_word_results = word_result_handler.exact_word_results.copy()
        word_result_handler0.other_word_results = word_result_handler.other_word_results.copy()
        word_result_handler0.matching_results = word_result_handler.matching_results.copy()
        word_result_handler0.display_queue = word_result_handler.display_queue.copy()
        word_result_handler0.display_count = word_result_handler.display_count
        return word_result_handler0

    @classmethod
    def sample(self, num_samples: int=1) -> list:
        word_result_handler_list = []
        for i in range(num_samples):
            word_result_handler = WordResultHandler()
            word_result_handler.specify_num_results(3*2)
            for j, word_result in enumerate(WordResult.sample(3*2)):
                word_result = WordResult.buffer(word_result)
                word_result.jap_vocab.writing = f'{word_result.jap_vocab.writing}_{i}_{j}'
                word_result.jap_vocab.reading = f'{word_result.jap_vocab.reading}_{i}_{j}'
                category = 'exact_matches' if j % 2 == 0 else 'other_matches'
                word_result_handler.add(word_result=word_result, category=category)
            word_result_handler_list.append(word_result_handler)
        return word_result_handler_list

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
