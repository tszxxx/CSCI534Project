import csv
import json

def analyze_Naive_Bayes():
    print('---------for Naive Bayes----------------')
    with open('../Naive_Bayes/nbmodel.csv') as input_file:
        spamreader = csv.reader(input_file, delimiter=',', quotechar='\"')
        cnt = 0
        whole_dict = {'relaxed': 0, 'angry': 0, 'happy': 0, 'sad': 0}
        for record in spamreader:
            if cnt > 0:
                each_dict = {'relaxed': record[1], 'angry': record[2], 'happy': record[3], 'sad': record[4]}
                whole_dict[max(each_dict, key=each_dict.get)] += 1
            cnt += 1

        for key in whole_dict:
            print(key, '%.2f' % (whole_dict[key] / cnt))

    with open('../Naive_Bayes/nboutput.csv') as input_file:
        spamreader = csv.reader(input_file, delimiter=',', quotechar='\"')
        cnt = 0
        whole_dict = {'relaxed': 0, 'angry': 0, 'happy': 0, 'sad': 0}
        for record in spamreader:
            if cnt > 0:
                whole_dict[record[2]] += 1
            cnt += 1

        for key in whole_dict:
            print(key, whole_dict[key])
    print('---------for Naive Bayes----------------')

def analyze_Perceptron():
    word_dict = {}
    print('---------for Perceptron-----------------')
    with open('../Perceptron/arousal_vanilla_model.txt') as input_file:
        perceptron_dict = json.loads(input_file.readline())
        for key in perceptron_dict:
            if key not in word_dict:
                word_dict[key] = {'arousal': 0.0, 'valence': 0.0}
            word_dict[key]['arousal'] += perceptron_dict[key] / 2

    with open('../Perceptron/arousal_averaged_model.txt') as input_file:
        perceptron_dict = json.loads(input_file.readline())
        for key in perceptron_dict:
            if key not in word_dict:
                word_dict[key] = {'arousal': 0.0, 'valence': 0.0}
            word_dict[key]['arousal'] += perceptron_dict[key] / 2

    with open('../Perceptron/valence_vanilla_model.txt') as input_file:
        perceptron_dict = json.loads(input_file.readline())
        for key in perceptron_dict:
            if key not in word_dict:
                word_dict[key] = {'arousal': 0.0, 'valence': 0.0}
            word_dict[key]['valence'] += perceptron_dict[key] / 2

    with open('../Perceptron/valence_averaged_model.txt') as input_file:
        perceptron_dict = json.loads(input_file.readline())
        for key in perceptron_dict:
            if key not in word_dict:
                word_dict[key] = {'arousal': 0.0, 'valence': 0.0}
            word_dict[key]['valence'] += perceptron_dict[key] / 2

    whole_dict = {'relaxed': 0, 'angry': 0, 'happy': 0, 'sad': 0}
    for key in word_dict:
        if word_dict[key]['arousal'] > 0.0 and word_dict[key]['valence'] > 0.0:
            whole_dict['happy'] += 1
        if word_dict[key]['arousal'] > 0.0 and word_dict[key]['valence'] < 0.0:
            whole_dict['angry'] += 1
        if word_dict[key]['arousal'] < 0.0 and word_dict[key]['valence'] > 0.0:
            whole_dict['relaxed'] += 1
        if word_dict[key]['arousal'] < 0.0 and word_dict[key]['valence'] < 0.0:
            whole_dict['sad'] += 1

    for key in whole_dict:
        print(key, ' %.2f' % (whole_dict[key] / sum(whole_dict.values())))

    file_dict = {}
    with open('../Perceptron/percepoutput_arousal_vanilla.csv') as input_file:
        spamreader = csv.reader(input_file, delimiter=',', quotechar='\"')
        cnt = 0
        for record in spamreader:
            if cnt > 0:
                if record[0] not in file_dict:
                    file_dict[record[0]] = {'arousal': 0, 'valence': 0}
                file_dict[record[0]]['arousal'] += (1 if record[2] == 'positive' else -1)
            cnt += 1

    with open('../Perceptron/percepoutput_arousal_average.csv') as input_file:
        spamreader = csv.reader(input_file, delimiter=',', quotechar='\"')
        cnt = 0
        for record in spamreader:
            if cnt > 0:
                if record[0] not in file_dict:
                    file_dict[record[0]] = {'arousal': 0, 'valence': 0}
                file_dict[record[0]]['arousal'] += (1 if record[2] == 'positive' else -1)
            cnt += 1

    with open('../Perceptron/percepoutput_valence_vanilla.csv') as input_file:
        spamreader = csv.reader(input_file, delimiter=',', quotechar='\"')
        cnt = 0
        for record in spamreader:
            if cnt > 0:
                if record[0] not in file_dict:
                    file_dict[record[0]] = {'arousal': 0, 'valence': 0}
                file_dict[record[0]]['valence'] += (1 if record[2] == 'positive' else -1)
            cnt += 1

    with open('../Perceptron/percepoutput_valence_average.csv') as input_file:
        spamreader = csv.reader(input_file, delimiter=',', quotechar='\"')
        cnt = 0
        for record in spamreader:
            if cnt > 0:
                if record[0] not in file_dict:
                    file_dict[record[0]] = {'arousal': 0, 'valence': 0}
                file_dict[record[0]]['valence'] += (1 if record[2] == 'positive' else -1)
            cnt += 1

    whole_dict = {'relaxed': 0, 'angry': 0, 'happy': 0, 'sad': 0}
    for key in file_dict:
        if file_dict[key]['arousal'] > 0 and file_dict[key]['valence'] > 0:
            whole_dict['happy'] += 1
        if file_dict[key]['arousal'] > 0 and file_dict[key]['valence'] < 0:
            whole_dict['angry'] += 1
        if file_dict[key]['arousal'] < 0 and file_dict[key]['valence'] > 0:
            whole_dict['relaxed'] += 1
        if file_dict[key]['arousal'] < 0 and file_dict[key]['valence'] < 0:
            whole_dict['sad'] += 1

    for key in whole_dict:
        print(key, whole_dict[key])
    print('---------for Perceptron-----------------')

def analyze_Syntax_Analysis():
    with open('../Syntax_Analysis/overall.csv', 'r') as input_file:
        syntax_dict = {}
        cnt = 0
        for line in input_file:
            if cnt > 0:
                record = line.strip().split(',')
                if record[1] == 'upos':
                    if record[2] not in syntax_dict:
                        syntax_dict[record[2]] = {'relaxed': 0, 'angry': 0, 'happy': 0, 'sad': 0}
                    each_dict = {'relaxed': record[6], 'angry': record[4], 'happy': record[3], 'sad': record[5]}
                    syntax_dict[record[2]][max(each_dict, key=each_dict.get)] += 1
            cnt += 1
        print('\t\trelaxed\tangry\thappy\tsad')
        for key in syntax_dict:
            print(key, end='\t')
            if len(key) < 4:
                print('\t', end='')
            for mood in syntax_dict[key]:
                print('%d' % (syntax_dict[key][mood] / sum(syntax_dict[key].values()) * 100), end='%\t\t')
            print()


if __name__ == '__main__':
    # analyze_Naive_Bayes()
    # analyze_Perceptron()
    analyze_Syntax_Analysis()