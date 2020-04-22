import csv
import cv2
import numpy as np
import os
import pywt
import matplotlib.pyplot as plt

def train_arousal_valence_model(input_dir_path, output_file_path):
    with open(input_dir_path + 'ABSTRACT_groundTruth.csv', 'r') as input_file:
        spamreader = csv.reader(input_file, delimiter=',', quotechar='\'')
        cnt = 0
        with open(output_file_path, 'w') as output_file:
            for record in spamreader:
                if cnt > 0:
                    file_path = input_dir_path + record[0]
                    bgrImage = cv2.imread(file_path)
                    rgbImage = cv2.cvtColor(bgrImage, cv2.COLOR_BGR2RGB)
                    hsvImage = cv2.cvtColor(rgbImage, cv2.COLOR_RGB2HSV)
                    mean_H = np.mean(hsvImage[:][:][0])
                    mean_S = np.mean(hsvImage[:][:][1])
                    mean_V = np.mean(hsvImage[:][:][2])
                    output_file.write(record[0] + ',' + str(mean_H) + ',' + str(mean_S) + ',' + str(mean_V)
                                      + ',' + str(0.69 * mean_V + 0.22 * mean_S)
                                      + ',' + str(-0.31 * mean_V + 0.60 * mean_S)
                                      + ',' + str(0.76 * mean_V + 0.32 * mean_S) + '\n')
                else:
                    output_file.write("file,mean H, mean S, mean V, pleasure, arousal, dominance\n")
                cnt += 1

def normalize_arousal_valence_model(input_file_path, output_file_path):
    file_name, pleasure, arousal, dominance = [], [], [], []
    with open(input_file_path, 'r') as input_file:
        cnt = 0
        for line in input_file:
            if cnt > 0:
                records = line.strip().split(',')
                file_name.append(records[0])
                pleasure.append(float(records[4]))
                arousal.append(float(records[5]))
                dominance.append(float(records[6]))
            cnt += 1
    with open(output_file_path, 'w') as output_file:
        output_file.write('file,arousal,valence\n')
        for i in range(len(file_name)):
            cur_pleasure = (pleasure[i] - min(pleasure)) / (max(pleasure) - min(pleasure))
            cur_arousal = (arousal[i] - min(arousal)) / (max(arousal) - min(arousal))
            cur_dominance = (dominance[i] - min(dominance)) / (max(dominance) - min(dominance))
            output_file.write(file_name[i] + ',' + str(cur_pleasure) + ',' + str(cur_arousal) + ',' + str(cur_dominance) + '\n')

def get_train_data(input_dir_path, normal_file_path, train_file_path):
    file_dict = {}
    with open(input_dir_path + 'ABSTRACT_groundTruth.csv', 'r') as input_file:
        spamreader = csv.reader(input_file, delimiter=',', quotechar='\'')
        cnt = 0
        labels = None
        for record in spamreader:
            if cnt > 0:
                mood_dict = {}
                for (i, value) in enumerate(record):
                    mood_dict[labels[i]] = value if i == 0 else int(value)
                file_name = mood_dict.pop('file_path')
                file_dict[file_name] = {'mood': max(mood_dict, key=mood_dict.get)}
            else:
                labels = record
                labels[0] = 'file_path'
            cnt += 1

    with open(normal_file_path, 'r') as input_file:
        spamreader = csv.reader(input_file, delimiter=',', quotechar='\'')
        cnt = 0
        for record in spamreader:
            if cnt > 0:
                file_name = record[0]
                file_dict[file_name]['pleasure'] = record[1]
                file_dict[file_name]['arousal'] = record[2]
                file_dict[file_name]['dominance'] = record[3]
            cnt += 1

    with open(train_file_path, 'w') as output_file:
        output_file.write('file name,pleasure,arousal,dominance,mood\n')
        for key in file_dict:
            output_file.write(key
                              + ',' + file_dict[key]['pleasure']
                              + ',' + file_dict[key]['arousal']
                              + ',' + file_dict[key]['dominance']
                              + ',' + file_dict[key]['mood'] + '\n')

def train_wavelet_model(input_dir_path, output_file_path):
    with open(input_dir_path + 'ABSTRACT_groundTruth.csv', 'r') as input_file:
        spamreader = csv.reader(input_file, delimiter=',', quotechar='\'')
        cnt = 0
        with open(output_file_path, 'w') as output_file:
            for record in spamreader:
                if cnt > 0:
                    file_path = input_dir_path + record[0]
                    bgrImage = cv2.imread(file_path)
                    rgbImage = cv2.cvtColor(bgrImage, cv2.COLOR_BGR2RGB)
                    hsvImage = cv2.cvtColor(rgbImage, cv2.COLOR_RGB2HSV)
                    H, S, V = hsvImage[:][:][0], hsvImage[:][:][1], hsvImage[:][:][2]
                    coeffs_H = pywt.wavedec2(H, 'db1', level=3)
                    c_H_1, c_H_2, c_H_3 = np.mean(coeffs_H[0]), np.mean(coeffs_H[1]), np.mean(coeffs_H[2])
                    Sum_H = c_H_1 + c_H_2 + c_H_3
                    
                    coeffs_S = pywt.wavedec2(S, 'db1', level=3)
                    c_S_1, c_S_2, c_S_3 = np.mean(coeffs_S[0]), np.mean(coeffs_S[1]), np.mean(coeffs_S[2])
                    Sum_S = c_S_1 + c_S_2 + c_S_3
                    
                    coeffs_V = pywt.wavedec2(V, 'db1', level=3)
                    c_V_1, c_V_2, c_V_3 = np.mean(coeffs_V[0]), np.mean(coeffs_V[1]), np.mean(coeffs_V[2])
                    Sum_V = c_V_1 + c_V_2 + c_V_3
                    output_file.write(record[0] + ',{},{},{},{},{},{},{},{},{},{},{},{}\n'.format(
                        str(c_H_1), str(c_H_2), str(c_H_3),
                        str(c_S_1), str(c_S_2), str(c_S_3),
                        str(c_V_1), str(c_V_2), str(c_V_3),
                        str(Sum_H), str(Sum_S), str(Sum_V)))
                else:
                    output_file.write('file name,c_H_1,c_H_2,c_H_3,c_S_1,c_S_2,c_S_3,c_V_1,c_V_2,c_V_3,Sum_H,Sum_S,Sum_V\n')
                cnt += 1

if __name__ == '__main__':
    input_dir_path = '/Users/hangjiezheng/Downloads/testImages_abstract/'
    output_file_path = 'output.csv'
    if not os.path.exists(output_file_path):
        train_arousal_valence_model(input_dir_path, output_file_path)
    normal_file_path = 'normal.csv'
    if not os.path.exists(normal_file_path):
        normalize_arousal_valence_model(output_file_path, normal_file_path)
    os.remove(output_file_path)
    train_file_path = 'train_data.csv'
    if not os.path.exists(train_file_path):
        get_train_data(input_dir_path, normal_file_path, train_file_path)
    os.remove(normal_file_path)
    wavelet_file_path = 'train_wavelet.csv'
    if not os.path.exists(wavelet_file_path):
        train_wavelet_model(input_dir_path, wavelet_file_path)

