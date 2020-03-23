import csv
import chardet
import string
import json
import os
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
        coefficient = vanilla_dict.get(token, 0) - average_dict[token] / total_samples
        if coefficient != 0:
            final_average_dict[token] = coefficient
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        output_file.write(json.dumps(final_average_dict))
        output_file.write('\n')
        output_file.write(str(final_average_bias))

def test_perceptron_valence(test_file_path, test_dir_path, valence_dict, valence_bias, output_file_path):
    global stop_words, table
    all_token = []
    test_dir_path += '/'
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        with open(test_file_path, 'r', encoding='utf-8') as test_file:
            cnt = 0
            spamreader = csv.reader(test_file, delimiter=',', quotechar='\"')
            for records in spamreader:
                if cnt > 0:
                    input_file_path = test_dir_path + records[0] + '.txt'
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
                    if mood == 'happy' or mood == 'relaxed':
                        output_file.write(records[0] + ',' + 'positive' + ',')
                    else:
                        output_file.write(records[0] + ',' + 'negative' + ',')

                    res = valence_bias
                    for token in all_token:
                        res += valence_dict.get(token, 0)
                    if res > 0:
                        output_file.write('positive' + '\n')
                    else:
                        output_file.write('negative' + '\n')
                else:
                    output_file.write('Index,Actual Valence,Predicted Valence\n')
                cnt += 1

def test_perceptron_arousal(test_file_path, test_dir_path, arousal_dict, arousal_bias, output_file_path):
    global stop_words, table
    all_token = []
    test_dir_path += '/'
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        with open(test_file_path, 'r', encoding='utf-8') as test_file:
            cnt = 0
            spamreader = csv.reader(test_file, delimiter=',', quotechar='\"')
            for records in spamreader:
                if cnt > 0:
                    input_file_path = test_dir_path + records[0] + '.txt'
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
                    if mood == 'happy' or mood == 'angry':
                        output_file.write(records[0] + ',' + 'positive' + ',')
                    else:
                        output_file.write(records[0] + ',' + 'negative' + ',')

                    res = arousal_bias
                    for token in all_token:
                        res += arousal_dict.get(token, 0)
                    if res > 0:
                        output_file.write('positive' + '\n')
                    else:
                        output_file.write('negative' + '\n')
                else:
                    output_file.write('Index,Actual Arousal,Predicted Arousal\n')
                cnt += 1

def calc_f1score(input_file_path_prefix, mid, postfix):
    input_file_path = input_file_path_prefix + mid + postfix
    true_positive, false_positive, false_negative, true_negative = 0, 0, 0, 0
    with open(input_file_path, 'r', encoding='utf-8') as input_file:
        cnt = 0
        for line in input_file:
            if cnt > 0:
                token = line.split(',')
                if token[1] == 'positive':
                    if token[2].strip() == 'positive':
                        true_positive += 1
                    else:
                        false_negative += 1
                else:
                    if token[2].strip() == 'positive':
                        false_positive += 1
                    else:
                        true_negative += 1
            cnt += 1
    precision = true_positive / (true_positive + false_positive)
    recall = true_positive / (true_positive + false_negative)
    print('for' + mid.replace('_', ' '), ':')
    print('\tprecison:\t', precision)
    print('\trecall:\t', recall)
    print('\tf1_score:\t', 2 * precision * recall / (precision + recall))
 
def input_perceptron(perceptron_model_path):
    with open(perceptron_model_path, 'r', encoding='utf-8') as input_file:
        perceptron_dict = json.loads(input_file.readline())
        perceptron_bias = float(input_file.readline())
        return perceptron_dict, perceptron_bias

if __name__ == '__main__':
    train_balanced_file_path = '../train/MoodyLyrics/ml_balanced.csv'
    train_dir_path = '../train/words'

    if not os.path.exists('arousal_vanillamodel.txt') \
        or not os.path.exists('arousal_averagedmodel.tx') \
        or not os.path.exists('valence_vanillamodel.tx') \
        or not os.path.exists('valence_averagedmodel.tx'):
        arousal_train_data, valence_train_data = get_train_content(train_balanced_file_path, train_dir_path)

        arousal_vanilla_dict, arousal_vanilla_bias, arousal_average_dict, arousal_average_bias \
            = train_perceptron(arousal_train_data, 100)
        valence_vanilla_dict, valence_vanilla_bias, valence_average_dict, valence_average_bias \
            = train_perceptron(valence_train_data, 100)

        output_vanilla('arousal_vanillamodel.txt', arousal_vanilla_dict, arousal_vanilla_bias)
        output_average('arousal_averagedmodel.txt', arousal_average_dict, arousal_average_bias, arousal_vanilla_dict, arousal_vanilla_bias, 100 * 2 * len(arousal_train_data[0]))
        output_vanilla('valence_vanillamodel.txt', valence_vanilla_dict, valence_vanilla_bias)
        output_average('valence_averagedmodel.txt', valence_average_dict, valence_average_bias, valence_vanilla_dict, valence_vanilla_bias, 100 * 2 * len(valence_train_data[0]))

    arousal_vanilla_dict, arousal_vanilla_bias = input_perceptron('arousal_vanillamodel.txt')
    arousal_average_dict, arousal_average_bias = input_perceptron('arousal_averagedmodel.txt')
    valence_vanilla_dict, valence_vanilla_bias = input_perceptron('valence_vanillamodel.txt')
    valence_average_dict, valence_average_bias = input_perceptron('valence_averagedmodel.txt')

    test_file_path = '../test/balanced.csv'
    test_dir_path = '../test/words'
    output_file_path = 'percepoutput'
    test_perceptron_arousal(test_file_path, test_dir_path, arousal_vanilla_dict, arousal_vanilla_bias,
                            output_file_path + '_arousal' + '_vanialla' + '.csv')
    test_perceptron_arousal(test_file_path, test_dir_path, arousal_average_dict, arousal_average_bias,
                            output_file_path + '_arousal' + '_average' + '.csv')
    test_perceptron_valence(test_file_path, test_dir_path, valence_vanilla_dict, valence_vanilla_bias,
                            output_file_path + '_valence' + '_vanialla' + '.csv')
    test_perceptron_valence(test_file_path, test_dir_path, valence_average_dict, valence_average_bias,
                            output_file_path + '_valence' + '_average' + '.csv')
    calc_f1score(output_file_path, '_arousal' + '_vanialla', '.csv')
    calc_f1score(output_file_path, '_arousal' + '_average', '.csv')
    calc_f1score(output_file_path, '_valence' + '_vanialla', '.csv')
    calc_f1score(output_file_path, '_valence' + '_average', '.csv')
