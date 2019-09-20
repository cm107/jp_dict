from .jap_vocab import JapaneseVocab
from .concept import ConceptLabels
from .vocab_entry import VocabularyEntry
from ..util.previews import yellow_text, blue_text, green_text, std_text

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
            print(yellow_text + 'results found: {}'.format(self.num_results) + std_text)
        for word_result in self.display_queue:
            self.display_count += 1
            print_str = yellow_text + '========================result {}======================='.format(self.display_count) + std_text + '\n'
            print_str += green_text + '{}'.format(word_result) + std_text
            print(print_str)
        self.display_queue = []

# word_result_handler = WordResultHandler()