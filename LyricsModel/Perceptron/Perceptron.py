import csv
import chardet
import string
import json
from random import shuffle

table = str.maketrans('', '', string.punctuation)
stop_words = {'ourselves', 'hers', 'between', 'yourself', 'but', 'again', 'there', 'about', 'once', 'during', 'out', 'very', 'having', 'with', 'they', 'own', 'an', 'be', 'some', 'for', 'do', 'its', 'yours', 'such', 'into', 'of', 'most', 'itself', 'other', 'off', 'is', 's', 'am', 'or', 'who', 'as', 'from', 'him', 'each', 'the', 'themselves', 'until', 'below', 'are', 'we', 'these', 'your', 'his', 'through', 'don', 'nor', 'me', 'were', 'her', 'more', 'himself', 'this', 'down', 'should', 'our', 'their', 'while', 'above', 'both', 'up', 'to', 'ours', 'had', 'she', 'all', 'no', 'when', 'at', 'any', 'before', 'them', 'same', 'and', 'been', 'have', 'in', 'will', 'on', 'does', 'yourselves', 'then', 'that', 'because', 'what', 'over', 'why', 'so', 'can', 'did', 'not', 'now', 'under', 'he', 'you', 'herself', 'has', 'just', 'where', 'too', 'only', 'myself', 'which', 'those', 'i', 'after', 'few', 'whom', 't', 'being', 'if', 'theirs', 'my', 'against', 'a', 'by', 'doing', 'it', 'how', 'further', 'was', 'here', 'than'} 

def get_train_content(train_file_path, train_dir_path):
    global stop_words, table
    arousal_train_data = [[], []]
    valence_train_data = [[], []]
    train_dir_path += '/'
    with open(train_file_path, 'r', encoding='utf-8') as train_file:
        cnt = 0
        spamreader = csv.reader(train_file, delimiter=',', quotechar='\"')
        for records in spamreader:
            if cnt > 0:
                input_file_path = train_dir_path + records[0] + '.txt'
                all_token = []
                encoding = ''
                with open(input_file_path, 'rb') as input_file:
                    data = input_file.read()
                    encoding = chardet.detect(data)
                with open(input_file_path, 'r', encoding=encoding['encoding']) as input_file:
                    for line in input_file:
                        tokens = line.split()
                        for token in tokens:
                            token = token.translate(table).lower().strip()
                            if len(token) > 0 and token not in stop_words and token not in all_token:
                                all_token.append(token)
                mood = records[3].lower()
                if mood == 'happy':
                    arousal_train_data[1].append(all_token)
                    valence_train_data[1].append(all_token)
                if mood == 'angry':
                    arousal_train_data[1].append(all_token)
                    valence_train_data[0].append(all_token)
                if mood == 'sad':
                    arousal_train_data[0].append(all_token)
                    valence_train_data[0].append(all_token)
                if mood == 'relaxed':
                    arousal_train_data[0].append(all_token)
                    valence_train_data[1].append(all_token)
            cnt += 1

    return arousal_train_data, valence_train_data

def train_perceptron_per_file(tokens, classifer, vanilla_dict, vanilla_bias, average_dict, average_bias, iter_time):
    res = vanilla_bias
    for token in tokens:
        res += vanilla_dict.setdefault(token, 0)
    if classifer == 1:
        if res <= 0:
            average_bias += iter_time
            vanilla_bias += 1
            for token in tokens:
                vanilla_dict[token] = vanilla_dict.get(token, 0) + 1
                average_dict[token] = average_dict.get(token, 0) + iter_time
    else:
        if res >= 0:
            average_bias -= iter_time
            vanilla_bias -= 1
            for token in tokens:
                vanilla_dict[token] = vanilla_dict.get(token, 0) - 1
                average_dict[token] = vanilla_dict.get(token, 0) - iter_time
    return vanilla_bias, average_bias

def train_perceptron_once(train_data, vanilla_dict, vanilla_bias, average_dict, average_bias, iter_time):
    global all_train_data
    shuffle(train_data[0])
    shuffle(train_data[1])
    size = len(train_data[0])
    iter_time = iter_time * 2 * size

    for i in range(size):
        vanilla_bias, average_bias = train_perceptron_per_file(train_data[0][i], 0, vanilla_dict, vanilla_bias, average_dict, average_bias, iter_time + 2 * i)
        vanilla_bias, average_bias = train_perceptron_per_file(train_data[1][i], 1, vanilla_dict, vanilla_bias, average_dict, average_bias, iter_time + 2 * i + 1)

def train_perceptron(train_data, Maxiter):
    vanilla_dict, average_dict = {}, {}
    vanilla_bias, average_bias = 0, 0
    for i in range(Maxiter):
        train_perceptron_once(train_data, vanilla_dict, vanilla_bias, average_dict, average_bias, i)
    return vanilla_dict, vanilla_bias, average_dict, average_bias

def output_vanilla(output_file_path, vanilla_dict, vanilla_bias):
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        keys = list(vanilla_dict.keys())
        for token in keys:
            if vanilla_dict[token] == 0:
                del vanilla_dict[token]
        output_file.write(json.dumps(vanilla_dict))
        output_file.write('\n')
        output_file.write(str(vanilla_bias))

def output_average(output_file_path, average_dict, average_bias, vanilla_dict, vanilla_bias, total_samples):
    final_average_dict = {}
    final_average_bias = vanilla_bias - average_bias / total_samples
    for token in average_dict:
        coefficient = vanilla_dict[token] - average_dict[token] / total_samples
        if coefficient != 0:
            final_average_dict[token] = coefficient
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        output_file.write(json.dumps(final_average_dict))
        output_file.write('\n')
        output_file.write(str(final_average_bias))

if __name__ == '__main__':
    train_balanced_file_path = '../train/MoodyLyrics/ml_balanced.csv'
    train_dir_path = '../train/words'
    arousal_train_data, valence_train_data = get_train_content(train_balanced_file_path, train_dir_path)

    arousal_vanilla_dict, arousal_vanilla_bias, arousal_average_dict, arousal_average_bias \
        = train_perceptron(arousal_train_data, 100)
    valence_vanilla_dict, valence_vanilla_bias, valence_average_dict, valence_average_bias \
        = train_perceptron(valence_train_data, 100)

    output_vanilla('arousal_vanillamodel.txt', arousal_vanilla_dict, arousal_vanilla_bias)
    output_average('arousal_averagedmodel.txt', arousal_vanilla_dict, arousal_average_bias, arousal_vanilla_dict, arousal_vanilla_bias, 100 * 2 * len(arousal_train_data[0]))
    output_vanilla('valence_vanillamodel.txt', valence_vanilla_dict, valence_vanilla_bias)
    output_average('valence_averagedmodel.txt', valence_vanilla_dict, valence_average_bias, valence_vanilla_dict, valence_vanilla_bias, 100 * 2 * len(valence_train_data[0]))