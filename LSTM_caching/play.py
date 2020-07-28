import numpy as np
import pandas as pd
import pickle
from sklearn.preprocessing import MinMaxScaler
import argparse
import os
trained = [1, 10, 100, 1003, 1004, 1005, 1006, 1007, 1008, 1009, 101, 1010, 1011, 1012, 1013, 1014, 1015, 1016, 1017, 1018, 1019, 1020, 1021, 1022, 1023, 1024, 1025, 1027, 1028, 1029, 1030, 1031, 1032, 1033, 1034, 1035, 1036, 1037, 1038, 104, 1040, 1041, 1042, 1043, 1044, 1046, 1047, 1049, 105, 1050, 1051, 1053, 1054, 1055, 1056, 1057, 1058, 1059, 1060, 107, 11, 110, 111, 112, 122, 125, 135, 14, 140, 141, 144, 145, 147, 150, 151, 153, 154, 155, 156, 157, 158, 159, 16, 160, 161, 162, 163, 164, 165, 166, 168, 169, 17, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 18, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 19, 190, 191, 193, 194, 195, 196, 198, 199, 2, 200, 204, 208, 21, 216, 22, 223, 224, 225, 230, 231, 235, 236, 24, 246, 247, 25, 252, 253, 256, 260, 261, 265, 266, 272, 277, 282, 288, 29, 292, 293, 296, 3, 300, 31, 315, 316, 317, 318, 32, 329, 333, 337, 339, 34, 342, 344, 345, 348, 349, 350, 353, 355, 356, 357, 36, 364, 367, 368, 370, 372, 376, 377, 380, 39, 41, 410, 420, 431, 432, 434, 435, 44, 440, 441, 442, 45, 454, 455, 457, 466, 47, 471, 474, 475, 48, 480, 485, 49272, 494, 497, 5, 50, 500, 508, 509, 515, 52, 520, 524, 527, 529, 53, 539, 54, 541, 543, 55, 551, 552, 553, 555, 57, 58, 585, 586, 587, 588, 589, 59, 590, 592, 593, 594, 595, 596, 597, 6, 60, 605, 608, 609, 61, 610, 613, 616, 62, 628, 63, 637, 6377, 64, 640, 647, 648, 65, 653, 66, 661, 662, 663, 67, 671, 673, 674, 678, 68, 688, 69, 694, 7, 70, 703, 704, 705, 707, 708, 709, 71, 710, 711, 714, 715, 718, 719, 72, 720, 722, 724, 725, 726, 728, 73, 731, 732, 733, 735, 736, 737, 74, 741, 743, 745, 748, 75, 750, 76, 761, 762, 765, 778, 780, 781, 782, 783, 784, 785, 786, 788, 79, 798, 799, 801, 802, 804, 805, 808, 809, 81, 810, 818, 82, 828, 829, 830, 832, 833, 835, 836, 837, 838, 839, 842, 848, 849, 85, 851, 852, 854, 858, 86, 860, 861, 862, 866, 867, 869, 870, 875, 876, 877, 879, 88, 880, 881, 882, 885, 886, 888, 89, 891, 892, 893, 896, 897, 898, 899, 900, 903, 904, 908, 910, 911, 912, 913, 914, 915, 916, 917, 918, 919, 92, 920, 921, 922, 923, 924, 926, 928, 93, 930, 931, 932, 933, 934, 936, 938, 94, 940, 942, 943, 944, 945, 946, 947, 948, 949, 95, 950, 951, 952, 953, 954, 955, 96, 968, 969, 97, 99, 994]


class PredictPop:

    def __init__(self):
        self.model_path = 'models'
        self.data_path = 'data'

    @staticmethod
    def get_model(filename):
        # load the model from disk
        file = open(filename, 'rb')
        loaded_model = pickle.load(file)
        file.close()
        return loaded_model

    @staticmethod
    def predict_next(model, data):
        scaler = MinMaxScaler(feature_range=(0, 1))

        history = np.array(data)
        dataset = scaler.fit_transform(history)
        # Scale the data to be values between 0 and 1
        # scaled_history = scaler.transform(history)
        # Create an empty list
        X_test = [dataset]
        # Convert the X_test data set to a numpy array
        X_test = np.array(X_test)

        X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))

        pred_value = model.predict(X_test)
        # undo the scaling
        pred_value = scaler.inverse_transform(pred_value)
        return pred_value[0][0]

    def process_request(self, request, t_time):
        if request in trained:
            model = self.get_model(f'{self.model_path}/model{request}.sav')
            raw_data = pd.read_csv(f'{self.data_path}/{request}.csv')
            stop = np.where(raw_data['timestamp'] == t_time)[0][-1]
            if stop >= 80:
                data = list(raw_data['rating'].values[stop-80:stop])
                data = [[i] for i in data]
                return self.predict_next(model=model, data=data)
            else:
                print(f'not enough -> {stop}')
        else:
            print(f'not in trained {request}')
        return 0


def main():
    parser = argparse.ArgumentParser()   # --n=5
    parser.add_argument('--r', type=int, default=1, help='request')
    parser.add_argument('--t', type=str, default=1, help='timestamp')
    args = parser.parse_args()

    ans = PredictPop().process_request(args.r, args.t)
    os.system(f'echo "{ans}" > out.txt')


if __name__ == '__main__':
    main()
