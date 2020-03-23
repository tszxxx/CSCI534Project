import sys
import os
import re
import string
import time
from random import shuffle

vanilla_pn_dict, average_pn_dict = {}, {}
vanilla_td_bias, average_td_bias = 0, 0
vanilla_td_dict, average_td_dict = {}, {}
vanilla_pn_bias, average_pn_bias = 0, 0
all_train_data = {'positive':[], 'negative':[], 'truthful':[], 'deceptive':[]}
stop_words = {'ourselves', 'hers', 'between', 'yourself', 'but', 'again', 'there', 'about', 'once', 'during', 'out', 'very', 'having', 'with', 'they', 'own', 'an', 'be', 'some', 'for', 'do', 'its', 'yours', 'such', 'into', 'of', 'most', 'itself', 'other', 'off', 'is', 's', 'am', 'or', 'who', 'as', 'from', 'him', 'each', 'the', 'themselves', 'until', 'below', 'are', 'we', 'these', 'your', 'his', 'through', 'don', 'nor', 'me', 'were', 'her', 'more', 'himself', 'this', 'down', 'should', 'our', 'their', 'while', 'above', 'both', 'up', 'to', 'ours', 'had', 'she', 'all', 'no', 'when', 'at', 'any', 'before', 'them', 'same', 'and', 'been', 'have', 'in', 'will', 'on', 'does', 'yourselves', 'then', 'that', 'because', 'what', 'over', 'why', 'so', 'can', 'did', 'not', 'now', 'under', 'he', 'you', 'herself', 'has', 'just', 'where', 'too', 'only', 'myself', 'which', 'those', 'i', 'after', 'few', 'whom', 't', 'being', 'if', 'theirs', 'my', 'against', 'a', 'by', 'doing', 'it', 'how', 'further', 'was', 'here', 'than'} 

def get_train_content(file_path, positive_negative, truthful_deceptive):
    global all_train_data, stop_words

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

    all_train_data[positive_negative].append(all_token)
    all_train_data[truthful_deceptive].append(all_token)

def train_perceptron_perfile_truthful_deceptive(tokens, truthful_deceptive, iter_time):
    global vanilla_td_dict, average_td_dict
    global vanilla_td_bias, average_td_bias
    res_td = vanilla_td_bias
    for token in tokens:
        res_td += vanilla_td_dict.setdefault(token, 0)
    if truthful_deceptive == 'truthful':
        if res_td <= 0:
            average_td_bias += iter_time
            vanilla_td_bias += 1
            for token in tokens:
                vanilla_td_dict[token] = vanilla_td_dict.setdefault(token, 0) + 1
                average_td_dict[token] = average_td_dict.setdefault(token, 0) + iter_time
    else:
        if res_td >= 0:
            average_td_bias -= iter_time
            vanilla_td_bias -= 1
            for token in tokens:
                vanilla_td_dict[token] = vanilla_td_dict.setdefault(token, 0) - 1
                average_td_dict[token] = vanilla_td_dict.setdefault(token, 0) - iter_time

def train_perceptron_perfile_positive_negative(tokens, positive_negative, iter_time):
    global vanilla_pn_dict, average_pn_dict
    global vanilla_pn_bias, average_pn_bias
    res_pn = vanilla_pn_bias
    for token in tokens:
        res_pn += vanilla_pn_dict.setdefault(token, 0)
    if positive_negative == 'positive':
        if res_pn <= 0:
            average_pn_bias += iter_time
            vanilla_pn_bias += 1
            for token in tokens:
                vanilla_pn_dict[token] = vanilla_pn_dict.setdefault(token, 0) + 1
                average_pn_dict[token] = average_pn_dict.setdefault(token, 0) + iter_time
    else:
        if res_pn >= 0:
            average_pn_bias -= iter_time
            vanilla_pn_bias -= 1
            for token in tokens:
                vanilla_pn_dict[token] = vanilla_pn_dict.setdefault(token, 0) - 1
                average_pn_dict[token] = vanilla_pn_dict.setdefault(token, 0) - iter_time

def train_perceptron_once(iter_time):
    global all_train_data
    shuffle(all_train_data['positive'])
    shuffle(all_train_data['negative'])
    shuffle(all_train_data['truthful'])
    shuffle(all_train_data['deceptive'])
    size = len(all_train_data['positive'])
    iter_time = iter_time * 2 * size
    notChange = True

    for i in range(size):
        res = train_perceptron_perfile_positive_negative(all_train_data['positive'][i], 'positive', iter_time + 2 * i)
        notChange = notChange and res

        res =  train_perceptron_perfile_positive_negative(all_train_data['negative'][i], 'negative', iter_time + 2 * i + 1)
        notChange = notChange and res

        res =  train_perceptron_perfile_truthful_deceptive(all_train_data['truthful'][i], 'truthful', iter_time + 2 * i)
        notChange = notChange and res

        res =  train_perceptron_perfile_truthful_deceptive(all_train_data['deceptive'][i], 'deceptive', iter_time + 2 * i + 1)
        notChange = notChange and res
    
    return notChange

def train_perceptron(Maxiter):
    global all_train_data
    size = len(all_train_data['positive'])
    for i in range(Maxiter):
        if train_perceptron_once(i):
            break
    return (i + 1) * 2 * size

def output_vanilla(file):
    global vanilla_pn_dict, vanilla_pn_bias
    file.write('for positive/negative\n')
    file.write('bias:\t' + str(vanilla_pn_bias) + '\n')
    file.write('token' + '\t' + 'coefficient' + '\n')
    for token in vanilla_pn_dict:
        coefficient = vanilla_pn_dict[token]
        if coefficient != 0:
            file.write(token + '\t' + str(coefficient) + '\n')
            
    global vanilla_td_dict, vanilla_td_bias
    file.write('for truthful/deceptive\n')
    file.write('bias:\t' + str(vanilla_td_bias) + '\n')
    file.write('token'+'\t'+'coefficient'+'\n')
    for token in vanilla_td_dict:
        coefficient = vanilla_td_dict[token]
        if coefficient != 0:
            file.write(token + '\t' + str(coefficient) + '\n')
            
def output_average(file, total_samples):
    global average_pn_dict, average_pn_bias
    global vanilla_pn_dict, vanilla_pn_bias
    file.write('for positive/negative\n')
    file.write('bias:\t' + str(vanilla_pn_bias - average_pn_bias / total_samples) + '\n')
    file.write('token' + '\t' +'coefficient\n')
    for token in average_pn_dict:
        coefficient = vanilla_pn_dict[token] - average_pn_dict[token] / total_samples
        if coefficient != 0:
            file.write(token + '\t' + str(coefficient) + '\n')
            
    global average_td_dict, average_td_bias
    global vanilla_td_dict, vanilla_td_bias
    file.write('for truthful/deceptive\n')
    file.write('bias:\t' + str(vanilla_td_bias - average_td_bias / total_samples) + '\n')
    file.write('token' + '\t' +'coefficient\n')
    for token in average_td_dict:
        coefficient = vanilla_td_dict[token] - average_td_dict[token] / total_samples
        if coefficient != 0:
            file.write(token + '\t' + str(coefficient) + '\n')

if __name__ == '__main__':
    a = time.time()
    input_path = sys.argv[1]
    test_path_list = []
    for root,dirs,files in os.walk(input_path):
        for file in files:
            file_path = os.path.join(root,file)
            if file_path.find('.txt') != -1:
                if file_path.find('negative') != -1:
                    if file_path.find('deceptive') != -1:
                        if file_path.find('fold1') == -1:
                            get_train_content(file_path, 'negative', 'deceptive')
                        else:
                            test_path_list.append([file_path, 'negative', 'deceptive'])
                    elif file_path.find('truthful') != -1:
                        if file_path.find('fold1') == -1:
                            get_train_content(file_path, 'negative', 'truthful')
                        else:
                            test_path_list.append([file_path, 'negative', 'truthful'])
                elif file_path.find('positive') != -1:
                    if file_path.find('deceptive') != -1:
                        if file_path.find('fold1') == -1:
                            get_train_content(file_path, 'positive', 'deceptive')
                        else:
                            test_path_list.append([file_path, 'positive', 'deceptive'])
                    elif file_path.find('truthful') != -1:
                        if file_path.find('fold1') == -1:
                            get_train_content(file_path, 'positive', 'truthful')
                        else:
                            test_path_list.append([file_path, 'positive', 'truthful'])

    total_samples = train_perceptron(100)
    b = time.time()

    output_file = open("vanillamodel.txt","w")    
    output_vanilla(output_file)
    output_file.close()

    output_file = open("averagedmodel.txt","w")    
    output_average(output_file, total_samples)
    output_file.close()