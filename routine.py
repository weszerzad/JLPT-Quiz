import os
import json
from send_email import send_email

def get_info(mondai_dict):

    frequency = mondai_dict['frequency']
    img_path = mondai_dict['img_path']
    audio_url = mondai_dict['audio_url']
    test_name = img_path.split('/')[3]
    mondai_name = img_path.split('/')[4].replace('.jpg', '')

    return test_name, mondai_name, img_path, audio_url, frequency

# load data
with open('data.json') as f:
    data = json.load(f)

#load mondai_dict_list stream
with open('mondai_dict_list.json', 'r') as f:
    mondai_dict_list = json.load(f)

for count, mondai_dict in enumerate(mondai_dict_list):

    if mondai_dict != None:

        test_name, mondai_name, img_path, audio_url, frequency = get_info(mondai_dict)

        FILEPATH_AND_FILENAME_DICT = {}
        FILEPATH_AND_FILENAME_DICT[img_path] = test_name + ' ' + mondai_name + '.jpg'
        if audio_url != '':
            FILEPATH_AND_FILENAME_DICT[audio_url] = test_name + ' ' + mondai_name + '.mp3'

        EMAIL_SUBJECT = '{0} {1} ({2}/{3})'.format(test_name, mondai_name, count + 1, len(mondai_dict_list))
        MESSAGE_BODY = '''GOOD LUCK!'''

        send_email(EMAIL_SUBJECT, os.environ['EMAIL_FROM'], os.environ['EMAIL_TO'], MESSAGE_BODY,
                   FILEPATH_AND_FILENAME_DICT, os.environ['SMTP_USERNAME'],
                   os.environ['SMTP_PASSWORD'])

        # increase frequency by 1
        data['test'][test_name][mondai_name]['frequency'] += 1

        # remove it from the list
        mondai_dict_list[count] = None

        # save to the db
        with open('mondai_dict_list.json', 'w') as outfile:
            json.dump(mondai_dict_list, outfile)
        with open('data.json', 'w') as outfile:
            json.dump(data, outfile)

        break