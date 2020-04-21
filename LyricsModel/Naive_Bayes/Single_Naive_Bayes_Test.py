import os
import autocorrect
import string
import math

def get_naive_bayes_model(nbmodel_file_path):
    words_dict = {}
    # speller = autocorrect.Speller(lang='en')

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

def test_naive_bayes_model(input_file_path, words_dict):
    table = str.maketrans('', '', string.punctuation)
    with open(input_file_path, 'r') as input_file:
        possibility_dict = {
            'relaxed': 0,
            'angry': 0,
            'happy': 0,
            'sad': 0
        }
        for line in input_file:
            tokens = line.split()
            for token in tokens:
                token = token.translate(table).lower().strip()
                if token in words_dict:
                    total = sum(words_dict[token].values())
                    for mood in words_dict[token]:
                        possibility_dict[mood] += math.log2(words_dict[token][mood] / total)

    return max(possibility_dict, key=possibility_dict.get)


if __name__ == '__main__':
    nbmodel_file_path = 'nbmodel.csv'
    word_dict = get_naive_bayes_model(nbmodel_file_path)
    input_file_path = '../Modify_Test/input.csv'
    output_file_dir = '../Modify_Test/output/'
    output_file_path = '../Modify_Test/output.csv'
    algorithms = ['syntax', 'WordEmbedding']
    cnt = 0
    with open(output_file_path, 'w') as output_file:
        output_file.write('file path,expected mood,result mood\n')
        with open(input_file_path, 'r', encoding='utf-8') as input_file:
            for line in input_file:
                if cnt > 0:
                    record = line.strip().split(',')
                    name, path, source_mood, target_mood = record[0], record[1], record[2], record[3]
                    for algorithm in algorithms:
                        test_file_path = output_file_dir + algorithm + '_' + name
                        output_file.write(test_file_path + ',' + target_mood + ',' + test_naive_bayes_model(test_file_path, word_dict) + '\n')
                cnt += 1
