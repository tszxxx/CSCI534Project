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
        keys = list(model_dict['upos'][upos].keys())
        random.shuffle(keys)
        for word in keys:
            if model_dict['upos'][upos][word] == expected_label:
                changed_words += 1
                return word
    return lemma

def get_model_dict(model_file_path, threshold=100):
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
    return model_dict

def replace_word(input_file_path, model_dict, output_file_path, expected_label, table, nlp):
    with open(input_file_path, 'r', encoding='utf-8') as input_file:
        with open(output_file_path, 'w', encoding='utf-8') as output_file:
            for line in input_file:
                line = re.sub(r'\([^\)]*\)', '', line)
                line = re.sub(r'\[[^\]]*\]', '', line)
                line = line.translate(table).strip()
                if len(line) > 0:
                    doc = nlp(line)
                    for sent in doc.sentences:
                        for word in sent.words:
                            output_file.write(
                                find_replace_word(word.lemma, word.upos, word.xpos, model_dict,
                                                  expected_label) + ' ')
                    output_file.write('\n')

def replace_word_by_csv(input_file_path, model_dict, output_file_dir):
    table = str.maketrans('', '', string.punctuation)
    nlp = stanza.Pipeline(processors='tokenize,lemma,mwt,pos')
    if not os.path.exists(output_file_dir):
        os.mkdir(output_file_dir)
    output_file_dir += '/'
    with open(input_file_path, 'r', encoding='utf-8') as input_file:
        input_cnt = 0
        for line in input_file:
            if input_cnt > 0:
                record = line.strip().split(',')
                name, path, original_label, expected_label = record[0], record[1], record[2], record[3]
                output_file_path = output_file_dir + 'syntax_' + name
                replace_word(path + name, model_dict, output_file_path, expected_label, table, nlp)
            input_cnt += 1

if __name__ == '__main__':
    input_file_path = len(sys.argv) > 1 is not None and sys.argv[1] or '../Modify_Test/input.csv'
    model_file_path = len(sys.argv) > 2 is not None and sys.argv[2] or 'overall.csv'
    output_file_dir = len(sys.argv) > 3 is not None and sys.argv[3] or '../Modify_Test/output'
    model_dict = get_model_dict(model_file_path, threshold=10)
    replace_word_by_csv(input_file_path, model_dict, output_file_dir)
    print('has changed about', changed_words, 'words')
