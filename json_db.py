import json
import os
from natsort import natsorted

def add_test(data_test, test_path):

    test_name = os.path.basename(test_path)

    d = {}

    audio_mondai_list = ["聴解 問題1", "聴解 問題2", "聴解 問題3", "聴解 問題4", "聴解 問題5"]

    with open('filtered_data_file.json') as f:
        mondai_name_list = json.load(f)

    for i in mondai_name_list:

        if i in audio_mondai_list:
            audio_path = test_path + '/' + i + '.mp3'
        else:
            audio_path = ''

        d[i] = {'frequency': 0,
                'img_path': test_path + '/' + i + '.jpg',
                'audio_url': audio_path
                }

    data_test[test_name] = d

if __name__ == "__main__":

    path = "/Users/phuocpham/OneDrive - Shizuoka University/pythonProject/pdf/code_base/pdf_files"
    l = [f for f in os.listdir(path) if f.endswith('Test')]
    l = natsorted(l)

    #initiate data
    data = {}
    data['test'] = {}

    # #load data
    # with open('data.json') as f:
    #     data = json.load(f)

    for e in l:
        #get test path
        test_path = "/code_base/pdf_files/{}".format(e)
        if test_path.endswith('/'):
            test_path = test_path[:-1]

        #add test to data
        add_test(data['test'], test_path)

    #save data
    with open('data.json', 'w') as outfile:
        json.dump(data, outfile)