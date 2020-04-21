import csv
import math
import cv2
import numpy as np
import os

def calDistance(a, b):
    return math.sqrt(sum((a-b) ** 2))

def train_image_abstract_model(input_dir_path, output_dir_path, output_file_path):
    if not os.path.exists(output_dir_path):
        os.mkdir(output_dir_path)
    output_dir_path += '/'
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
                    output_file.write(record[0] + ',' + str(mean_H) + ',' + str(mean_S) + ',' + str(mean_V) + ',' + str(-0.31 * mean_V + 0.60 * mean_S) + ',' + str(0.69 * mean_V + 0.22 * mean_S) + '\n')
                else:
                    output_file.write("file,mean H, mean S, mean V, arousal, valence\n")
                cnt += 1

if __name__ == '__main__':
    input_dir_path = '/Users/hangjiezheng/Downloads/testImages_abstract/'
    output_dir_path = 'hsv'
    output_file_path = 'output.csv'
    train_image_abstract_model(input_dir_path, output_dir_path, output_file_path)