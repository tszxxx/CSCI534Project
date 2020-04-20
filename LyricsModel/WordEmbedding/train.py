import os
from gensim.models import Word2Vec, KeyedVectors
import csv
import chardet

def get_model(balance_file_path, input_file_dir, model_file_dir):
    arr = []
    input_file_dir += '/'
    with open(balance_file_path, 'r', encoding='utf-8') as balance_file:
        cnt = 0
        spamreader = csv.reader(balance_file, delimiter=',', quotechar='\"')
        for record in spamreader:
            if cnt > 0:
                file_path = input_file_dir + record[0] + '.txt'
                encoding = ''
                with open(file_path, 'rb') as file:
                    data = file.read()
                    encoding = chardet.detect(data)
                with open(file_path, 'r', encoding=encoding['encoding']) as file:
                    tokens = file.read().replace("\n", " ").split(" ")
                tokens.append(record[-1])
                arr.append(tokens)
                print(cnt)
            cnt += 1
    model_file_dir += '/'
    for i in range(100, 300, 50):
        model_file_path = model_file_dir + 'model' + str(i) + '.wv'
        model = Word2Vec(arr, min_count=1, size=200, window=5)
        model.wv.save(model_file_path)
        del model

if __name__ == '__main__':
    balance_file_path = '../train/MoodyLyrics/ml_balanced.csv'
    input_file_dir = '../train/words'
    model_file_dir = 'model'
    if not os.path.exists(model_file_dir):
        os.mkdir(model_file_dir)
    get_model(balance_file_path, input_file_dir, model_file_dir)
