import os
import autocorrect
import string
import math

def test_naive_bayes_model(input_file_path, nbmodel_file_path, output_file_path):
    words_dict = {}
    # speller = autocorrect.Speller(lang='en')
    table = str.maketrans('', '', string.punctuation)

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
    with open(output_file_path, 'w') as output_file:
        output_file.write(max(possibility_dict, key=possibility_dict.get))


if __name__ == '__main__':
    nbmodel_file_path = 'nbmodel.csv'
    file_path = 'ML1.txt'
    input_file_path = '../Syntax_Analysis/output/' + file_path
    if not os.path.exists('../Syntax_Analysis/test'):
        os.mkdir('../Syntax_Analysis/test')
        print()
    output_file_path = '../Syntax_Analysis/test/' + file_path
    test_naive_bayes_model(input_file_path, nbmodel_file_path, output_file_path)
