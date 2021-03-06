import cv2
import numpy as np
import os
import pywt
import csv
from skimage.feature import greycomatrix, greycoprops
from ThirdParty import tamura_numpy

label_dict = {
    'amusement': {'arousal': 'positive', 'valence': 'positive'},
    'anger': {'arousal': 'positive', 'valence': 'negative'},
    'awe': {'arousal': 'positive', 'valence': 'negative'},
    'content': {'arousal': 'negative', 'valence': 'positive'},
    'contentment': {'arousal': 'negative', 'valence': 'positive'},
    'disgust': {'arousal': 'positive', 'valence': 'negative'},
    'excitement': {'arousal': 'positive', 'valence': 'positive'},
    'fear': {'arousal': 'positive', 'valence': 'negative'},
    'sad': {'arousal': 'negative', 'valence': 'negative'},
}
label_list = ['Amusement', 'Anger', 'Awe', 'Content', 'Disgust', 'Excitement', 'Fear', 'Sad']
color_dict = {
    'black': [0, 0, 0],
    'blue': [0, 0, 255],
    'brown': [165, 42, 42],
    'green': [0, 255, 0],
    'gray': [128, 128, 128],
    'orange': [255, 165, 0],
    'pink': [255, 192, 203],
    'purple': [128, 0, 128],
    'red': [255, 0, 0],
    'white': [255, 255, 255],
    'yellow': [255, 255, 0]
}

def get_arousal_valence_per_image(rgbImage):
    hsvImage = cv2.cvtColor(rgbImage, cv2.COLOR_RGB2HSV)
    mean_H = np.mean(hsvImage[:][:][0])
    mean_S = np.mean(hsvImage[:][:][1])
    mean_V = np.mean(hsvImage[:][:][2])
    return '%f,%f,%f,%f,%f,%f' % (mean_H, mean_S, mean_V,
                                 0.69 * mean_V + 0.22 * mean_S,
                                 -0.31 * mean_V + 0.60 * mean_S,
                                 0.76 * mean_V + 0.32 * mean_S)

def get_wavelet_per_image(rgbImage):
    hsvImage = cv2.cvtColor(rgbImage, cv2.COLOR_RGB2HSV)
    H, S, V = hsvImage[:][:][0], hsvImage[:][:][1], hsvImage[:][:][2]
    coeffs_H = pywt.wavedec2(H, 'db1', level=3)
    c_H_1, c_H_2, c_H_3 = np.mean(coeffs_H[1]), np.mean(coeffs_H[2]), np.mean(coeffs_H[3])
    Sum_H = c_H_1 + c_H_2 + c_H_3

    coeffs_S = pywt.wavedec2(S, 'db1', level=3)
    c_S_1, c_S_2, c_S_3 = np.mean(coeffs_S[1]), np.mean(coeffs_S[2]), np.mean(coeffs_S[3])
    Sum_S = c_S_1 + c_S_2 + c_S_3

    coeffs_V = pywt.wavedec2(V, 'db1', level=3)
    c_V_1, c_V_2, c_V_3 = np.mean(coeffs_V[1]), np.mean(coeffs_V[2]), np.mean(coeffs_V[3])
    Sum_V = c_V_1 + c_V_2 + c_V_3
    return '%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f' % (c_H_1, c_H_2, c_H_3,
                                                    c_S_1, c_S_2, c_S_3,
                                                    c_V_1, c_V_2, c_V_3,
                                                    Sum_H, Sum_S, Sum_V)

def get_color_name_per_image(rgbImage):
    global color_dict

    tmp_color_dict = {}
    tmp_distance_dict = {}
    for key in color_dict:
        tmp_color_dict[key] = 0
    for row in range(rgbImage.shape[0]):
        for col in range(rgbImage.shape[1]):
            for key in color_dict:
                tmp_distance_dict[key] = np.linalg.norm(rgbImage[row][col]-color_dict[key])
            tmp_color_dict[max(tmp_distance_dict, key=tmp_distance_dict.get)] += 1
    return ','.join([str(val) for val in tmp_color_dict.values()])

def get_color_features_from_file(input_file_path):
    bgrImage = cv2.imread(input_file_path)
    rgbImage = cv2.cvtColor(bgrImage, cv2.COLOR_BGR2RGB)
    return get_arousal_valence_per_image(rgbImage) + ',' + get_wavelet_per_image(rgbImage) + ',' + get_color_name_per_image(rgbImage)

def get_texture_features_per_image(greyImage):
    g = greycomatrix(greyImage, [1, 2], [0, np.pi/2])
    contrast = greycoprops(g, 'contrast').ravel()
    dissimilarity = greycoprops(g, 'dissimilarity').ravel()
    homogeneity = greycoprops(g, 'homogeneity').ravel()
    energy = greycoprops(g, 'energy').ravel()
    correlation = greycoprops(g, 'correlation').ravel()
    return ','.join([str(val) for val in contrast]) + ',' + \
           ','.join([str(val) for val in dissimilarity]) + ',' + \
           ','.join([str(val) for val in homogeneity]) + ',' + \
           ','.join([str(val) for val in energy]) + ',' + \
           ','.join([str(val) for val in correlation])

def get_other_features_per_image(greyImage):
    coar = tamura_numpy.coarseness(greyImage, kmax=5)
    cont = tamura_numpy.contrast(greyImage)
    dire = tamura_numpy.directionality(greyImage)
    return '%f,%f,%f' % (coar, cont, dire)

def get_other_features_from_file(input_file_path):
    rgbImage = cv2.imread(input_file_path)
    greyImage = cv2.cvtColor(rgbImage, cv2.COLOR_BGR2GRAY)
    return get_other_features_per_image(greyImage)

def get_texture_features_from_file(input_file_path):
    bgrImage = cv2.imread(input_file_path)
    rgbImage = cv2.cvtColor(bgrImage, cv2.COLOR_BGR2RGB)
    hsvImage = cv2.cvtColor(rgbImage, cv2.COLOR_RGB2HSV)
    return get_texture_features_per_image(hsvImage[:][:][0]) + ',' + \
           get_texture_features_per_image(hsvImage[:][:][1]) + ',' + \
            get_texture_features_per_image(hsvImage[:][:][2])

def get_mood_from_record(record):
    global label_list
    mood_dict = {}
    for (i, value) in enumerate(record):
        mood_dict[label_list[i]] = int(value)
    return max(mood_dict, key=mood_dict.get)

def get_data_from_file(label_dict, input_file_path):
    X, y = [], []
    with open(input_file_path, 'r') as input_file:
        cnt = 0
        for line in input_file:
            if cnt > 0:
                x = line.strip().split(',')
                label = x.pop().lower()
                if label == 'contentment':
                    label = 'content'
                y.append(label_dict[label])
                x.pop(0)
                x = [float(val) for val in x]
                X.append(x)
            cnt += 1
    return X, y

def build_data_from_lists(file_list, file_path_list, mood_list, output_dir):
    color_features_file = open(output_dir + 'color_features.csv', 'w')
    texture_features_file = open(output_dir + 'texture_features.csv', 'w')
    mood_features_file = open(output_dir + 'mood_features.csv', 'w')

    cnt = 0
    color_features_file.write("file,mean H,mean S,mean V,pleasure,arousal,dominance,c_H_1,c_H_2,c_H_3,c_S_1,c_S_2,c_S_3,c_V_1,c_V_2,c_V_3,Sum_H,Sum_S,Sum_V\n")
    texture_features_file.write("file,contrast,contrast,contrast,contrast,dissimilarity,dissimilarity,dissimilarity,dissimilarity,homogeneity,homogeneity,homogeneity,homogeneity,energy,energy,energy,energy,correlation,correlation,correlation,correlation\n")
    mood_features_file.write("file,mood\n")

    for value in zip(file_list, file_path_list, mood_list):
        cnt += 1
        print(cnt)
        color_features_file.write(value[0] + ',' + get_color_features_from_file(value[1]) + '\n')
        texture_features_file.write(value[0] + ',' + get_texture_features_from_file(value[1]) + '\n')
        mood_features_file.write(value[0] + ',' + value[2] + '\n')

    color_features_file.close()
    texture_features_file.close()
    mood_features_file.close()

def build_train_data(train_dir='train/'):
    input_dir_path = '/Users/hangjiezheng/Downloads/testImages_artphoto'
    file_list, file_path_list, mood_list = [], [], []
    for root, dirs, files in os.walk(input_dir_path):
        files.sort()
        for file in files:
            if file != 'ReadMe.rtf' and file != '.DS_Store':
                file_list.append(file)
                file_path_list.append(os.path.join(root, file))
                mood_list.append(file.split('_')[0])
    build_data_from_lists(file_list, file_path_list, mood_list, train_dir)

def build_test_data(test_dir='test/'):
    input_dir_path = '/Users/hangjiezheng/Downloads/testImages_abstract/'
    input_file_name = 'ABSTRACT_groundTruth.csv'
    file_list, file_path_list, mood_list = [], [], []

    with open(input_dir_path + input_file_name, 'r') as input_file:
        spamreader = csv.reader(input_file, delimiter=',', quotechar='\'')
        cnt = 0
        for records in spamreader:
            if cnt > 0:
                file_list.append(records[0])
                file_path_list.append(input_dir_path + records[0])
                mood_list.append(get_mood_from_record(records[1:]))
            cnt += 1
    build_data_from_lists(file_list, file_path_list, mood_list, test_dir)

def transform_data_from_file(input_file_dir):
    global label_dict
    files = ['color_features.csv', 'texture_features.csv', 'other_features.csv', 'mood_features.csv']
    final_input_file = input_file_dir + files.pop()
    X, arousal_y, valence_y = [], [], []
    for file in files:
        with open(input_file_dir + file, 'r') as input_file:
            spamreader = csv.reader(input_file, delimiter=',', quotechar='\'')
            cnt = 0
            for records in spamreader:
                if cnt > 0:
                    if cnt > len(X):
                        X.append(records[1:])
                    else:
                        X[cnt - 1].extend(records[1:])
                cnt += 1

    with open(final_input_file, 'r') as input_file:
        spamreader = csv.reader(input_file, delimiter=',', quotechar='\'')
        cnt = 0
        for records in spamreader:
            if cnt > 0:
                arousal_y.append(1 if label_dict[records[-1].lower()]['arousal'] == 'positive' else 0)
                valence_y.append(1 if label_dict[records[-1].lower()]['valence'] == 'positive' else 0)
            cnt += 1
    return X, arousal_y, valence_y

def train_several_model(train_file_dir, test_file_dir):
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler
    from sklearn.tree import DecisionTreeClassifier
    import warnings
    warnings.filterwarnings('ignore')
    scaler = StandardScaler()

    train_x, train_arousal_y, train_valence_y = transform_data_from_file(train_file_dir)
    scaler.fit(train_x)
    train_x = scaler.transform(train_x)

    test_x, test_arousal_y, test_valence_y = transform_data_from_file(test_file_dir)
    scaler.fit(test_x)
    test_x = scaler.transform(test_x)
    print('method\tdataset\tattribute\tscore')

    logistic_reg = LogisticRegression(random_state=0).fit(train_x, train_arousal_y)
    print('logistic regression\ttrain\tarousal\t%.2f' % logistic_reg.score(train_x, train_arousal_y))
    print('logistic regression\ttest\tarousal\t%.2f' % logistic_reg.score(test_x, test_arousal_y))
    del logistic_reg

    logistic_reg = LogisticRegression(random_state=0).fit(train_x, train_valence_y)
    print('logistic regression\ttrain\tvalence\t%.2f' % logistic_reg.score(train_x, train_valence_y))
    print('logistic regression\ttest\tvalence\t%.2f' % logistic_reg.score(test_x, test_valence_y))
    del logistic_reg

    tree_clf = DecisionTreeClassifier().fit(train_x, train_arousal_y)
    print('decision tree\ttrain\tarousal\t%.2f' % tree_clf.score(train_x, train_arousal_y))
    print('decision tree\ttest\tarousal\t%.2f' % tree_clf.score(test_x, test_arousal_y))
    del tree_clf

    tree_clf = DecisionTreeClassifier().fit(train_x, train_valence_y)
    print('decision tree\ttrain\tvalence\t%.2f' % tree_clf.score(train_x, train_valence_y))
    print('decision tree\ttest\tvalence\t%.2f' % tree_clf.score(test_x, test_valence_y))
    del tree_clf

def get_other_features_by_files_train():
    train_dir = 'train/'
    input_dir_path = '/Users/hangjiezheng/Downloads/testImages_artphoto'
    other_features_file_path = train_dir + 'other_features.csv'
    cur_line = 0
    if os.path.exists(other_features_file_path):
        with open(other_features_file_path, 'r') as input_file:
            cur_line = len(input_file.readlines())
    with open(other_features_file_path, 'a+') as output_file:
        if cur_line == 0:
            output_file.write('file,coarseness,contrast,directionality\n')
        for root, dirs, files in os.walk(input_dir_path):
            files.sort()
            cnt = 0
            for file in files:
                if file != 'ReadMe.rtf' and file != '.DS_Store':
                    if cnt >= cur_line - 1:
                        file_path = os.path.join(root, file)
                        output_file.write(file + ',' + get_other_features_from_file(file_path) + '\n')
                    cnt += 1
                    print(cnt)

def get_other_features_by_files_test():
    test_dir = 'test/'
    input_dir_path = '/Users/hangjiezheng/Downloads/testImages_abstract/'
    input_file_name = 'ABSTRACT_groundTruth.csv'
    other_features_file_path = test_dir + 'other_features.csv'
    with open(input_dir_path + input_file_name, 'r') as input_file:
        spamreader = csv.reader(input_file, delimiter=',', quotechar='\'')
        cnt = 0
        with open(other_features_file_path, 'w') as output_file:
            output_file.write('file,coarseness,contrast,directionality\n')
            for records in spamreader:
                if cnt > 0:
                    file_path = input_dir_path + records[0]
                    output_file.write(records[0] + ',' + get_other_features_from_file(file_path) + '\n')
                    print(cnt)
                cnt += 1

if __name__ == '__main__':
    #build_train_data()
    #build_test_data()
    #get_other_features_by_files_train()
    #get_other_features_by_files_test()
    train_several_model('train/', 'test/')



