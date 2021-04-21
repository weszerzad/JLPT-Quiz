import json
from random import shuffle
import os

# load data
with open('/Users/phuocpham/OneDrive - Shizuoka University/pythonProject/pdf/code_base/data.json') as f:
    data = json.load(f)

# create a list to save dicts of mondai in each test
mondai_dict_list = []
# create a list of test name
test_name_list = data['test'].keys()
for test_name in test_name_list:
    # create a list of mondai name
    mondai_name_list = data['test'][test_name].keys()
    for mondai_name in mondai_name_list:
        # only get the mondai with the specified frequency
        if data['test'][test_name][mondai_name]['frequency'] < 1:
            mondai_dict_list.append(data['test'][test_name][mondai_name])

shuffle(mondai_dict_list)

# print("Current Working Directory ", os.getcwd())

try:
    # Change the current working Directory
    os.chdir("/Users/phuocpham/OneDrive - Shizuoka University/pythonProject/pdf/code_base/")
except OSError:
    print("Can't change the Current Working Directory")

with open('mondai_dict_list.json', 'w') as f:
    json.dump(mondai_dict_list, f)

# print("Current Working Directory " , os.getcwd())