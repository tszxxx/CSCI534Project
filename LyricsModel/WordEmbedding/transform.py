from gensim.models import KeyedVectors
import os
import chardet
import string
import re

def load_nbmodel(nbmodel_file_path):
    words_dict = {}
    with open(nbmodel_file_path, 'r') as nbmodel_file:
        cnt = 0
        moods = []
        for line in nbmodel_file:
            if cnt > 0:
                tokens = line.split(',')
                words_dict[tokens[0]] = {}
                for i in range(len(moods)):
                    words_dict[tokens[0]][moods[i].strip()] = int(tokens[i + 1].strip())
            else:
                moods = line.split(',')[1:]
                cnt += 1
    return words_dict

def tranform(model_wv, nbmodel, input_file_path, output_file_dir, source_mood, target_mood, threshold=20):
    encoding = ''
    with open(input_file_path, 'rb') as input_file:
        data = input_file.read()
        encoding = chardet.detect(data)

    table = str.maketrans('', '', string.punctuation)
    with open(input_file_path, 'r', encoding=encoding['encoding']) as input_file:
        with open(output_file_dir + 'WordEmbedding_' + input_file_path.split('/')[-1], 'w') as output_file:
            for line in input_file:
                line = re.sub(r'\([^\)]*\)', '', line)
                line = re.sub(r'\[[^\]]*\]', '', line)
                line = line.translate(table).strip()
                if len(line) > 0:
                    tokens = line.strip().split(" ")
                    res = []
                    for token in tokens:
                        if token in model_wv:
                            val = model_wv[token] - model_wv[source_mood] + model_wv[target_mood]
                            arr = model_wv.similar_by_vector(val)
                            isFound = False
                            for [item, value] in arr:
                                if item in nbmodel and nbmodel[item][target_mood] - nbmodel[item][source_mood] >= threshold:
                                    res.append(item)
                                    isFound = True
                                    break
                            if not isFound:
                                res.append(token)
                        else:
                            res.append(token)
                    output_file.write(" ".join(res) + '\n')

if __name__ == '__main__':
    model_file_path = 'model/model100.wv'
    model_wv = KeyedVectors.load(model_file_path)
    input_file_path = '../Modify_Test/input.csv'
    output_file_dir = '../Modify_Test/output'
    nbmodel_file_path = '../Naive_Bayes/nbmodel.csv'
    nbmodel = load_nbmodel(nbmodel_file_path)
    if not os.path.exists(output_file_dir):
        os.mkdir(output_file_dir)
    output_file_dir += '/'
    with open(input_file_path, 'r', encoding='utf-8') as input_file:
        input_cnt = 0
        for line in input_file:
            if input_cnt > 0:
                record = line.strip().split(',')
                name, path, source_mood, target_mood = record[0], record[1], record[2], record[3]
                tranform(model_wv, nbmodel, path + name, output_file_dir, source_mood, target_mood)
            input_cnt += 1
