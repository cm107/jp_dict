class ConceptLabels:
    def __init__(self, is_common_word: bool, jlpt_level: int=None, wanikani_level: int=None):
        self.is_common_word = is_common_word
        self.jlpt_level = jlpt_level
        self.wanikani_level = wanikani_level

    def __str__(self):
        def append_str(first: bool, print_str: str, item: str) -> (bool, str):
            result_str = print_str
            if first:
                result_str += '{}'.format(item)
            else:
                result_str += ', {}'.format(item)
            return False, result_str

        print_str = 'Concept Labels:\n'
        first = True
        if self.is_common_word:
            print_str += 'Common Word'
            first = False
        if self.jlpt_level is not None:
            first, print_str = append_str(first, print_str, 'JLPT N{}'.format(self.jlpt_level))
        if self.wanikani_level is not None:
            first, print_str = append_str(first, print_str, 'WaniKani Level {}'.format(self.wanikani_level))
        
        print_str += '\n'
        return print_str

    def __repr__(self):
        return self.__str__()