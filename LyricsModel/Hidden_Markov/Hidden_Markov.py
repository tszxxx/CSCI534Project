import stanza
import csv
import chardet
import os
import re
import string

def create_dataset(input_file_path, train_data_dir, output_file_dir):
    # lemma, upos, xpos
    if not os.path.exists(output_file_dir):
        os.mkdir(output_file_dir)
    output_file_dir += '/'
    train_data_dir += '/'
    table = str.maketrans('','',string.punctuation)
    with open(input_file_path, 'r', encoding='utf-8') as input_file:
        spamreader = csv.reader(input_file, delimiter=',', quotechar='\"')
        cnt = 0
        word_dict = {}
        for record in spamreader:
            if cnt > 0:
                train_file_path = train_data_dir + record[0] + '.txt'
                encoding = None
                with open(train_file_path, 'rb') as input_file:
                    data = input_file.read()
                    encoding = chardet.detect(data)

                with open(train_file_path, 'r', encoding=encoding['encoding']) as input_file:
                    for line in input_file:
                        line = re.sub(r'\([^\)]*\)', '', line)
                        line = re.sub(r'\[[^\]]*\]', '', line)
                        line = line.translate(table).strip()
                        if len(line) > 0:
                            doc = nlp(line)
                            for sent in doc.sentences:
                                for word in sent.words:
                                    if word.lemma not in word_dict:
                                        word_dict[word.lemma] = {
                                            'upos': {},
                                            'xpos': {}
                                        }
                                    word_dict[word.lemma]['upos'][word.upos] = word_dict[word.lemma]['upos'].get(word.upos, 0) + 1
                                    word_dict[word.lemma]['xpos'][word.xpos] = word_dict[word.lemma]['xpos'].get(word.xpos, 0) + 1

                output_file_path = output_file_dir + record[0] + '.csv'
                with open(output_file_path, 'w', encoding='utf-8') as output_file:
                    output_file.write('Word,Method,Pos,Count\n')
                    for lemma in word_dict:
                        for method in word_dict[lemma]:
                            for token in word_dict[lemma][method]:
                                output_file.write(lemma + ',' + method + ',' + token + ',' + str(word_dict[lemma][method][token]) + '\n')
                print(cnt)
            cnt += 1

def get_statistic_result(input_file_path, tagging_file_dir, output_file_path):
    tagging_file_dir += '/'
    word_dict = {}
    with open(input_file_path, 'r', encoding='utf-8') as input_file:
        spamreader = csv.reader(input_file, delimiter=',', quotechar='\"')
        cnt = 0
        for record in spamreader:
            if cnt > 0:
                tagging_file_path = tagging_file_dir + record[0] + '.csv'
                with open(tagging_file_path, 'r', encoding='utf-8') as tagging_file:
                    another_cnt = 0
                    for line in tagging_file:
                        if another_cnt > 0:
                            tokens = line.split(',')
                            if tokens[0] not in word_dict:
                                word_dict[tokens[0]] = {}
                            if tokens[1] not in word_dict[tokens[0]]:
                                word_dict[tokens[0]][tokens[1]] = {}
                            word_dict[tokens[0]][tokens[1]][tokens[2]] = word_dict[tokens[0]][tokens[1]].get(tokens[2], 0) + 1
                        another_cnt += 1
                print(cnt)
            cnt += 1
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        output_file.write('Word,Method,Pos,Count\n')
        for lemma in word_dict:
            for method in word_dict[lemma]:
                for token in word_dict[lemma][method]:
                    output_file.write(
                        lemma + ',' + method + ',' + token + ',' + str(word_dict[lemma][method][token]) + '\n')

if __name__ == '__main__':
    # stanza.download('en')
    nlp = stanza.Pipeline(processors='tokenize,lemma,mwt,pos')
    input_file_path = '../train/MoodyLyrics/ml_balanced.csv'
    train_data_dir = '../train/lyrics'
    output_file_dir = '../train/tagging'
    if not os.path.exists(output_file_dir):
        create_dataset(input_file_path, train_data_dir, output_file_dir)
    output_file_path = 'overall.csv'
    if not os.path.exists(output_file_path):
        get_statistic_result(input_file_path, output_file_dir, output_file_path)
