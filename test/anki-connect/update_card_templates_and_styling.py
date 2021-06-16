from jp_dict.anki.connect import AnkiConnect

anki_connect = AnkiConnect()
anki_connect.update_parsed_vocab_templates_and_styling()
anki_connect.update_parsed_kanji_templates_and_styling()
anki_connect.save_changelog()