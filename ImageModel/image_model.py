import csv
from skimage import io
import math
import sys
import numpy as np

def calDistance(a, b):
    return math.sqrt(sum((a-b) ** 2))

def train_image_abstract_model(input_dir_path, output_file_path):
    color_dict = {
        'black': np.array([0, 0, 0]),
        'blue': np.array([0, 0, 255]),
        'brown': np.array([165, 42, 42]),
        'green': np.array([0, 255, 0]),
        'gray': np.array([128, 128, 128]),
        'orange': np.array([255, 128, 0]),
        'pink': np.array([255, 192, 20]),
        'purple': np.array([106, 13, 173]),
        'red': np.array([255, 0, 0]),
        'white': np.array([255, 255, 255]),
        'yellow': np.array([255, 255, 0])
    }
    with open(input_dir_path + 'ABSTRACT_groundTruth.csv', 'r') as input_file:
        spamreader = csv.reader(input_file, delimiter=',', quotechar='\'')
        cnt = 0
        label = None
        with open(output_file_path, 'w') as output_file:
            output_file.write(','.join(color_dict.keys()) + '\n')
            for record in spamreader:
                if cnt > 0:
                    file_path = input_dir_path + record[0]
                    arr = io.imread(file_path)
                    count_dict = {}
                    for row in range(arr.shape[0]):
                        for col in range(arr.shape[1]):
                            distance = sys.maxsize
                            color = None
                            for key in color_dict:
                                new_distance = calDistance(color_dict[key], arr[row][col])
                                if new_distance < distance:
                                    distance = new_distance
                                    color = key
                            count_dict[color] = count_dict.get(color, 0) + 1
                    count_arr = []
                    for key in color_dict:
                        count_arr.append(str(count_dict.get(key, 0)))
                    output_file.write(','.join(count_arr) + '\n')
                    print(cnt)
                else:
                    label = record
                cnt += 1

if __name__ == '__main__':
    input_dir_path = '/Users/hangjiezheng/Downloads/testImages_abstract/'
    output_file_path = 'Hue.csv'
    train_image_abstract_model(input_dir_path, output_file_path)