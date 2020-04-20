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
    main_dirs = ['../Syntax_Analysis', '../WordEmbedding']
    for main_dir in main_dirs:
        input_dir = main_dir + '/output/'
        output_dir = main_dir + '/test'
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        output_file_path = output_dir + '/output.csv'
        with open(output_file_path, 'w') as output_file:
            output_file.write('filename,mood\n')
            for root, dirs, files in os.walk(input_dir):
                for file in files:
                    output_file.write(file + ',' + test_naive_bayes_model(os.path.join(root, file), word_dict) + '\n')
