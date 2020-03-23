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

def test_perceptron_positive_negative(tokens, positive_negative):
    global perceptron_pn_dict, perceptron_pn_bias
    global pos_true_pos, pos_true_neg, pos_false_pos, pos_false_neg
    res_pn = perceptron_pn_bias

    for token in tokens:
        res_pn += perceptron_pn_dict.setdefault(token, 0)
    if positive_negative == 'positive':
        if res_pn <= 0:
            pos_false_neg += 1
        else:
            pos_true_pos += 1
    else:
        if res_pn >= 0:
            pos_false_pos += 1
        else:
            pos_true_neg += 1
    return res_pn

def test_perceptron(file_path, positive_negative, truthful_deceptive, output_file):
    global stop_words
    all_token = []
    file = open(file_path, 'r')
    line = file.readline()
    table = str.maketrans('','',string.punctuation)

    while line!='':
        tokens = re.split(r'[\.|\,|\ ]', line)
        for token in tokens:
            lowercase_token = token.translate(table).strip('\n')
            if lowercase_token not in all_token and lowercase_token != '' and lowercase_token not in stop_words and not re.search(r'\d', lowercase_token):
                all_token.append(lowercase_token)
        line = file.readline()
    file.close()
    res_td = test_perceptron_truthful_deceptive(all_token, truthful_deceptive)
    if res_td > 0:
        output_file.write('truthful\t')
    else:
        output_file.write('deceptive\t')

    res_pn = test_perceptron_positive_negative(all_token, positive_negative)
    if res_pn > 0:
        output_file.write('positive\t')
    else:
        output_file.write('negative\t')

    output_file.write(file_path.replace('\\','/') + '\n')

def calc_f1score(true_positive, false_positive, true_negative, false_negative):
    precision = true_positive / (true_positive + false_positive)
    recall = true_positive / (true_positive + false_negative)
    print('precison:\t', precision)
    print('recall:\t', recall)
    return 2 * precision * recall / (precision + recall)
 
def load_perceptron(model_path):
    global perceptron_pn_dict, perceptron_td_dict
    global perceptron_pn_bias, perceptron_td_bias
    cnt = 0
    file = open(model_path, 'r')
    line = file.readline()
    while line!='':
        if cnt == 0:
            cnt += 1
        elif cnt == 1:
            tokens = line.split()
            perceptron_pn_bias = float(tokens[1])
            cnt += 1
        elif cnt == 2:
            cnt += 1
        elif line == 'for truthful/deceptive\n':
            cnt = 4
        elif cnt == 3:
            tokens = line.split()
            perceptron_pn_dict[tokens[0]] = float(tokens[1])
        elif cnt == 4:
            tokens = line.split()
            perceptron_td_bias = float(tokens[1])
            cnt += 1
        elif cnt == 5:
            cnt += 1
        else:
            tokens = line.split()
            perceptron_td_dict[tokens[0]] = float(tokens[1])
        line = file.readline()

if __name__ == '__main__':
    model_path = sys.argv[1]
    input_path = sys.argv[2]
    output_file = open('percepoutput.txt', 'w')
    load_perceptron(model_path)
    for root,dirs,files in os.walk(input_path):
        for file in files:
            file_path = os.path.join(root,file)
            if file_path.find('.txt') != -1 and file_path.find('README') == -1 and file_path.find('fold1')!=-1:

                if file_path.find('positive')!=-1:
                    positive_negative = 'positive'
                else:
                    positive_negative = 'negative'

                if file_path.find('truthful')!=-1:
                    truthful_deceptive = 'truthful'
                else:
                    truthful_deceptive = 'deceptive'
                test_perceptron(file_path, positive_negative, truthful_deceptive, output_file)  
    output_file.close()    
    #print(b - a)
    #for [file, positive_negative, truthful_deceptive] in test_path_list:
    #    test_vanilla_perceptron(file, positive_negative, truthful_deceptive)

    #F1_1 = calc_f1score(pos_true_pos, pos_false_pos, pos_true_neg, pos_false_neg)
    #F1_2 = calc_f1score(pos_true_neg, pos_false_neg, pos_true_pos, pos_false_pos)
    #F2_1 = calc_f1score(truu_true_pos, truu_false_pos, truu_true_neg, truu_false_neg)
    #F2_2 = calc_f1score(truu_true_neg, truu_false_neg, truu_true_pos, truu_false_pos)

    #print(F1_1, F1_2, F2_1, F2_2)
    #print((F1_1 + F1_2 + F2_1 + F2_2) / 4)

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