import re
import sys
import chardet
import string
import stanza
import os
import random

changed_words = 0

def find_replace_word(lemma, upos, xpos, model_dict, expected_label):
    global changed_words
    if upos in model_dict['upos'] and lemma in model_dict['upos'][upos] and model_dict['upos'][upos][lemma] == expected_label:
        return lemma
    if upos in ['NOUN', 'VERB', 'ADJ', 'ADV']:
        keys =  list(model_dict['upos'][upos].keys())      # Python 3; use keys = d.keys() in Python 2
        random.shuffle(keys)
        for word in keys:
            if model_dict['upos'][upos][word] == expected_label:
                changed_words += 1
                return word
    return lemma


def replace_word(input_file_dir, input_file_path, model_file_path, output_file_dir, expected_label, threshold=100):
    nlp = stanza.Pipeline(processors='tokenize,lemma,mwt,pos')
    encoding = ''
    table = str.maketrans('','',string.punctuation)
    model_dict = {}
    with open(model_file_path, 'r', encoding='utf-8') as model_file:
        cnt = 0
        for line in model_file:
            if cnt > 0:
                tokens = line.strip().split(',')
                if tokens[1] not in model_dict:
                    model_dict[tokens[1]] = {}
                if tokens[2] not in model_dict[tokens[1]]:
                    model_dict[tokens[1]][tokens[2]] = {}
                tmp_dict = {
                    'happy': int(tokens[3]),
                    'angry': int(tokens[4]),
                    'sad': int(tokens[5]),
                    'relaxed': int(tokens[6])
                }
                min_mood, max_mood = min(tmp_dict, key=tmp_dict.get), max(tmp_dict, key=tmp_dict.get)
                if tmp_dict[max_mood] - tmp_dict[min_mood] > threshold:
                    model_dict[tokens[1]][tokens[2]][tokens[0]] = max_mood
            cnt += 1

    with open(input_file_dir + '/' + input_file_path, 'rb') as input_file:
        data = input_file.read()
        encoding = chardet.detect(data)
    if not os.path.exists(output_file_dir):
        os.mkdir(output_file_dir)
    output_file_path = output_file_dir + '/' + input_file_path
    with open(input_file_dir + '/' + input_file_path, 'r', encoding='utf-8') as input_file:
        with open(output_file_path, 'w', encoding='utf-8') as output_file:
            for line in input_file:
                line = re.sub(r'\([^\)]*\)', '', line)
                line = re.sub(r'\[[^\]]*\]', '', line)
                line = line.translate(table).strip()
                if len(line) > 0:
                    doc = nlp(line)
                    for sent in doc.sentences:
                        for word in sent.words:
                            output_file.write(find_replace_word(word.lemma, word.upos, word.xpos, model_dict, expected_label) + ' ')
                output_file.write('\n')

if __name__ == '__main__':
    input_file_dir = len(sys.argv) > 1 is not None and sys.argv[1] or 'input'
    model_file_path = len(sys.argv) > 2 is not None and sys.argv[2] or 'overall.csv'
    output_file_dir = len(sys.argv) > 3 is not None and sys.argv[3] or 'output'
    expected_label = len(sys.argv) > 4 is not None and sys.argv[4] or 'angry'
    for root, dirs, files in os.walk(input_file_dir):
        for input_file_path in files:
            replace_word(input_file_dir, input_file_path, model_file_path, output_file_dir, expected_label, threshold=10)
    print('has changed about', changed_words, 'words')