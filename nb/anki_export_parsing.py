import pickle
from src.submodules.logger.logger_handler import logger
from src.conf.paths import PathConf

suspicious_chars = list(' !"#$%&\'()~=~|`{+*}<<>?_1234567890-^\@[;:],./')

jlpt_all_notes_path = f"{PathConf.anki_dir}/jlpt_all_notes.txt"
jlpt_all_cards_path = f"{PathConf.anki_dir}/jlpt_all_cards.txt"
jlpt_all_notes_save_path = f"{PathConf.anki_dir}/jlpt_all_save.pkl"

anime_vocab_notes_path = f"{PathConf.anki_dir}/anime_vocab_notes.txt"
anime_vocab_cards_path = f"{PathConf.anki_dir}/anime_vocab_cards.txt"
anime_vocab_notes_save_path = f"{PathConf.anki_dir}/anime_vocab_save.pkl"

def clean_readings(readings: str) -> str:
    return (
        readings
        .replace('(more informal)', '')
        .replace('(more formal)', '')
        .replace(',&nbsp;', ', ')
    )

def process_readings(readings: str) -> list:
    readings = clean_readings(readings)
    return readings.split(', ')

def clean_vocab(vocab: str) -> str:
    return (
        vocab
        .replace(' (萎む)', '')
        .replace(' (呑気)', '')
    )

def process_vocab(vocab: str) -> str:
    vocab = clean_vocab(vocab)
    for char in vocab:
        if char in suspicious_chars:
            logger.red(vocab)
            break
    return vocab

anime_vocab_notes_data = open(anime_vocab_notes_path, 'r')
vocab_list = []
# for i, line in enumerate(anime_vocab_notes_data):
#     fields = line.split('\t')
#     vocab, readings, definition, eol = fields[0], fields[1], fields[2], fields[3:]
#     vocab = process_vocab(vocab)
#     readings = process_readings(readings)
#     eol = ''.join(eol)
#     definition = '\n'.join([definition, eol])
#     vocab_list.append(vocab)
for i, line in enumerate(anime_vocab_notes_data):
    fields = line.split('\t')
    vocab = fields[0]
    vocab = process_vocab(vocab)
    vocab_list.append(vocab)

for i, vocab in enumerate(vocab_list):
    logger.cyan(f"{i}: {vocab}")

pickle.dump(vocab_list, open(anime_vocab_notes_save_path, 'wb'))

jlpt_all_notes_data = open(jlpt_all_notes_path, 'r')
vocab_list = []
for i, line in enumerate(jlpt_all_notes_data):
    fields = line.split('\t')
    vocab = fields[0]
    vocab = process_vocab(vocab)
    vocab_list.append(vocab)

for i, vocab in enumerate(vocab_list):
    logger.cyan(f"{i}: {vocab}")

pickle.dump(vocab_list, open(jlpt_all_notes_save_path, 'wb'))