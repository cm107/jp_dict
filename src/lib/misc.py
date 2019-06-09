class Notes:
    def __init__(self, text: str):
        self.text = text

    def __str__(self):
        return self.text

    def __repr__(self):
        return self.__str__()

class Link:
    def __init__(self, text: str, url: str):
        self.text = text
        self.url = url

    def __str__(self):
        return '[{}]({})'.format(self.text, self.url)

    def __repr__(self):
        return self.__str__()