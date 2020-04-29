import os
import math
import autocorrect
import chardet
import csv
import string

table = str.maketrans('', '', string.punctuation)
stop_words = {'ourselves', 'hers', 'between', 'yourself', 'but', 'again', 'there', 'about', 'once', 'during', 'out', 'very', 'having', 'with', 'they', 'own', 'an', 'be', 'some', 'for', 'do', 'its', 'yours', 'such', 'into', 'of', 'most', 'itself', 'other', 'off', 'is', 's', 'am', 'or', 'who', 'as', 'from', 'him', 'each', 'the', 'themselves', 'until', 'below', 'are', 'we', 'these', 'your', 'his', 'through', 'don', 'nor', 'me', 'were', 'her', 'more', 'himself', 'this', 'down', 'should', 'our', 'their', 'while', 'above', 'both', 'up', 'to', 'ours', 'had', 'she', 'all', 'no', 'when', 'at', 'any', 'before', 'them', 'same', 'and', 'been', 'have', 'in', 'will', 'on', 'does', 'yourselves', 'then', 'that', 'because', 'what', 'over', 'why', 'so', 'can', 'did', 'not', 'now', 'under', 'he', 'you', 'herself', 'has', 'just', 'where', 'too', 'only', 'myself', 'which', 'those', 'i', 'after', 'few', 'whom', 't', 'being', 'if', 'theirs', 'my', 'against', 'a', 'by', 'doing', 'it', 'how', 'further', 'was', 'here', 'than'}

def train_naive_bayes_model(links_file_path, words_dir_path, words_option = 0, use_correct=False):
    global stop_words
    total_lines = 0
    with open(links_file_path, 'r', newline='', encoding='utf-8') as links_file:
        total_lines = len(links_file.readlines()) - 1
    words_dict = {}
    words_dir_path += '/'
    spller = autocorrect.Speller(lang='en')
    with open(links_file_path, 'r') as links_file:
        cnt = 0
        spamreader = csv.reader(links_file, delimiter=',', quotechar='\"')
        for record in spamreader:
            if cnt > 0:
                mood = record[3]
                input_file_path = words_dir_path + record[0] + '.txt'
                encoding = ''
                with open(input_file_path, 'rb') as input_file:
                    data = input_file.read()
                    encoding = chardet.detect(data)
                with open(input_file_path, 'r', encoding=encoding['encoding']) as input_file:
                    existing_words = set()
                    for line in input_file:
                        tokens = line.split()
                        for token in tokens:
                            token = token.translate(table).lower().strip()
                            if len(token) > 0 and token not in stop_words:
                                if use_correct:
                                    token = spller(token)
                                if token not in existing_words:
                                    if token not in words_dict:
                                        words_dict[token] = {
                                            'relaxed': 0,
                                            'angry': 0,
                                            'happy': 0,
                                            'sad': 0
                                        }
                                    words_dict[token][mood] += 1
                                if words_option != 0:
                                    existing_words.add(token)
                print(cnt, '/', total_lines, end='\n')
            cnt += 1
    return words_dict

def smooth_naive_bayes_model(words_dict):
    for token in words_dict:
        for mood in words_dict[token]:
            words_dict[token][mood] += 1

def output_naive_bayes_model(nbmodel_file_path, words_dict):
    try:
        with open(nbmodel_file_path, 'w') as nbmodel_file:
            nbmodel_file.write('word,relaxed,angry,happy,sad\n')
            for token in words_dict:
                nbmodel_file.write(token)
                for mood in words_dict[token]:
                    nbmodel_file.write(',' + str(words_dict[token][mood]))
                nbmodel_file.write('\n')
    except BaseException as e:
        os.remove(nbmodel_file_path)

def test_naive_bayes_model(links_file_path, words_dir_path, nbmodel_file_path, nboutput_file_path, words_option = 0, use_correct=False):
    words_dict = {}
    speller = autocorrect.Speller(lang='en')
    total_lines = 0
    with open(links_file_path, 'r', newline='', encoding='utf-8') as links_file:
        total_lines = len(links_file.readlines()) - 1

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
    with open(links_file_path, 'r') as links_file:
        with open(nboutput_file_path, 'w') as nboutput_file:
            cnt = 0
            words_dir_path += '/'
            spamreader = csv.reader(links_file, delimiter=',', quotechar='\"')
            for record in spamreader:
                if cnt > 0:
                    input_file_path = words_dir_path + record[0] + '.txt'
                    encoding = ''
                    possibility_dict = {
                        'relaxed': 0,
                        'angry': 0,
                        'happy': 0,
                        'sad': 0
                    }
                    with open(input_file_path, 'rb') as input_file:
                        data = input_file.read()
                        encoding = chardet.detect(data)
                    with open(input_file_path, 'r', encoding=encoding['encoding']) as input_file:
                        existing_words = set()
                        for line in input_file:
                            tokens = line.split()
                            for token in tokens:
                                token = token.translate(table).lower().strip()
                                if use_correct:
                                    token = speller(token)
                                if len(token) > 0 and token in words_dict:
                                    if token not in existing_words:
                                        total = sum(words_dict[token].values())
                                        for mood in words_dict[token]:
                                            possibility_dict[mood] += math.log2(words_dict[token][mood] / total)
                                    if words_option != 0:
                                        existing_words.add(token)
                        nboutput_file.write(record[0] + ',' + record[3] + ',' + max(possibility_dict, key=possibility_dict.get) + '\n')
                    print(cnt, '/', total_lines)
                else:
                    nboutput_file.write('Index,actual mood,predicted mood\n')
                cnt += 1

def calc_accuracy(nboutput_file_path):
    with open(nboutput_file_path, 'r') as nboutput_file:
        cnt = 0
        f1_dict = {}
        for line in nboutput_file:
            if cnt > 0 and len(line.split(',')) == 3:
                tokens = line.split(',')
                if tokens[1].strip() not in f1_dict:
                    f1_dict[tokens[1].strip()] = {
                        'relaxed': 0,
                        'angry': 0,
                        'happy': 0,
                        'sad': 0
                    }
                f1_dict[tokens[1].strip()][tokens[2].strip()] += 1
            cnt += 1
        print('label', 'precision', 'recall', 'f1-score',sep='\t')
        for certain_mood in ['relaxed', 'angry', 'happy', 'sad']:
            true_positive = 0
            false_positive = 0
            false_negative = 0
            true_negative = 0
            for actual_mood in f1_dict:
                if actual_mood.lower() == certain_mood.lower():
                    for predicted_mood in f1_dict[actual_mood]:
                        if predicted_mood.lower() == actual_mood.lower():
                            true_negative += f1_dict[actual_mood][predicted_mood]
                        else:
                            false_negative += f1_dict[actual_mood][predicted_mood]
                else:
                    for predicted_mood in f1_dict[actual_mood]:
                        if predicted_mood.lower() == actual_mood.lower():
                            true_positive += f1_dict[actual_mood][predicted_mood]
                        else:
                            false_positive += f1_dict[actual_mood][predicted_mood]
            precision = true_positive / (true_positive + false_positive)
            recall = true_positive / (true_positive + false_negative)
            print(certain_mood, '%.2f' % precision, '%.2f' % recall, '%.2f' % (2 * precision * recall / (precision + recall)), sep='\t')

if __name__ == '__main__':
    nbmodel_file_path = 'nbmodel.csv'
    train_file_path = '../train/MoodyLyrics/ml_balanced.csv'
    train_words_dir_path = '../train/words'
    if not os.path.exists(nbmodel_file_path):
        words_dict = train_naive_bayes_model(train_file_path, train_words_dir_path, words_option=0)
        smooth_naive_bayes_model(words_dict)
        output_naive_bayes_model(nbmodel_file_path, words_dict)
    nboutput_file_path = 'nboutput.csv'
    test_file_path = '../test/balanced.csv'
    test_words_dir_path =  '../test/words'
    if True or not os.path.exists(nboutput_file_path):
        test_naive_bayes_model(test_file_path, test_words_dir_path, nbmodel_file_path, nboutput_file_path, words_option=0)
    calc_accuracy(nboutput_file_path)