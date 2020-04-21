import csv
import math
import sys
import cv2
import numpy as np
import os

def calDistance(a, b):
    return math.sqrt(sum((a-b) ** 2))

def train_image_abstract_model(input_dir_path, output_dir_path):
    if not os.path.exists(output_dir_path):
        os.mkdir(output_dir_path)
    output_dir_path += '/'
    with open(input_dir_path + 'ABSTRACT_groundTruth.csv', 'r') as input_file:
        spamreader = csv.reader(input_file, delimiter=',', quotechar='\'')
        cnt = 0
        label = None
        for record in spamreader:
            if cnt > 0:
                file_path = input_dir_path + record[0]
                bgrImage = cv2.imread(file_path)
                rgbImage = cv2.cvtColor(bgrImage, cv2.COLOR_BGR2RGB)
                hsvImage = cv2.cvtColor(rgbImage, cv2.COLOR_RGB2HSV)
                cv2.imwrite(output_dir_path + record[0], hsvImage)
            else:
                label = record
            cnt += 1

if __name__ == '__main__':
    input_dir_path = '/Users/hangjiezheng/Downloads/testImages_abstract/'
    output_dir_path = 'hsv'
    train_image_abstract_model(input_dir_path, output_dir_path)