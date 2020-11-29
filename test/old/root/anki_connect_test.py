import json
import urllib.request
from common_utils.utils import beautify_dict

class AnkiConnectTest:
    def __init__(self):
        pass

    def request(self, action, **params):
        return {'action': action, 'params': params, 'version': 6}

    def invoke(self, action, **params):
        requestJson = json.dumps(self.request(action, **params)).encode("utf-8")
        response = json.load(urllib.request.urlopen(urllib.request.Request('http://localhost:8765', requestJson)))
        if len(response) != 2:
            raise Exception('response has an unexpected number of fields')
        if 'error' not in response:
            raise Exception('response is missing required error field')
        if 'result' not in response:
            raise Exception('response is missing required result field')
        if response['error'] is not None:
            raise Exception(response['error'])
        return response['result']

    def get_deck_names(self):
        result = self.invoke('deckNames')
        print('got list of decks: {}'.format(result))

    def get_version(self):
        result = self.invoke('version')
        print(f'version: {result}')

    def sync(self):
        self.invoke('sync')

    def get_decks(self):
        result = self.invoke('getDecks', cards=[1483987395981])
        print(result)

    def get_deck_config(self):
        result = self.invoke(action='getDeckConfig', deck='12 Anime Vocab (Non-JLPT) 01')
        print(result)

    def find_cards(self):
        result = self.invoke(action='findCards', query='deck:current')
        # print(result)
        return result

    def get_cards_info(self):
        card_ids = self.find_cards()
        result = self.invoke(action='cardsInfo', cards=card_ids)
        for card_info in result:
            # print(beautify_dict(data=card_info, indent=2))
            card_id = card_info['cardId']
            fields = card_info['fields']
            expression = fields['expression']
            reading = fields['reading']
            glossary = fields['glossary']
            sentence = fields['sentence']
            mnemonic = fields['mnemonic']
            field_order = card_info['fieldOrder']
            question = card_info['question']
            answer = card_info['answer']

            print(expression)

    def test(self):
        self.get_cards_info()

anki_connect_test = AnkiConnectTest()
anki_connect_test.test()
