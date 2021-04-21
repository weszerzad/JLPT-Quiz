import cv2
import pytesseract
from math import floor
import time
from pdf2image import convert_from_path
import numpy
import re
import os

key = None

buffer_img = 255 * numpy.ones((1, 1, 3), numpy.uint8)
buffer_name = "buffer img"

def timeit(func):
    """
    Decorator for measuring function's running time.
    """
    def measure_time(*args, **kw):
        start_time = time.time()
        result = func(*args, **kw)
        print("Processing time of %s(): %.2f seconds."
              % (func.__qualname__, time.time() - start_time))
        return result

    return measure_time

def convert_pil_to_cv2(pil_image):
    open_cv_image = numpy.array(pil_image)
    # Convert RGB to BGR
    open_cv_image = open_cv_image[:, :, ::-1].copy()
    return open_cv_image

def clean_quesiton_name(s):

    s = s.replace(' ', '')

    while not s[len(s)-1].isnumeric():
        s = s[:-1]

    return s

def clean_bracket_name(s):

    s = s.replace(' ', '')

    while not s.endswith(')'):
        s = s[:-1]

    return s

def is_question(s):
    return bool(re.search(r'^問題[0-9 ]+', s))

def number_between_bracket(s):
    return bool(re.search(r'^\([0-9 ]+\)$', s)) or bool(re.search(r'^\([0-9 ]+\) 以$', s))

def resize_img(img, x0=None, y0=None, x1=None, y1=None):

    # Set default value
    if x0 == None:
        x0 = 0
    if y0 == None:
        y0 = 0
    if x1 == None:
        x1 = img.shape[1]
    if y1 == None:
        y1 = img.shape[0]

    #Resize accordingly
    resized_img = img[y0:y1, x0:x1]

    return resized_img

def process_img(img):
    #gray, blur, thresh
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (7,7), 0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    # Create rectangular structuring element and dilate
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5,5))
    dilate = cv2.dilate(thresh, kernel, iterations=3)

    return [gray, blur, thresh, dilate]

def ocr(img, language='eng'):
    # configuration = '--psm 6 -c tessedit_char_whitelist={}'.format(key_char)
    configuration = '--psm 6'
    text = str(pytesseract.image_to_string(img, lang=language, config=configuration))
    return text

@timeit
def ROI(img, min_area, min_area_big, min_area_small, max_area):

    global section_count
    global mondai8_count
    global mondai9_count

    #Set up coordinate list
    line_items_coordinates = []
    coordinates_name = []

    #Get thresh image
    dilated_img = process_img(img)[3]

    #Find contours in a page
    crop_cnts = cv2.findContours(dilated_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    crop_cnts = crop_cnts[0] if len(crop_cnts) == 2 else crop_cnts[1]

    #show all contours
    # for crop_c in crop_cnts[::-1]:
    #     x, y, w, h = cv2.boundingRect(crop_c)
    #     # w = w + 75
    #     cv2.rectangle(img, (x, y), (x + w, y + h), (36, 255, 12), 2)

    #show only satisfied contours
    for crop_c in crop_cnts[::-1]:

        #get coordinate of each contour
        x, y, w, h = cv2.boundingRect(crop_c)
        # push contour edge to page right edge
        w = img.shape[1] - x

        #test
        # if True:
        #FIRST CONDITION: get the contour in the defined area range
        if min_area < w*h < max_area:
            #get the ocr of the contour
            roi = img[y:y+h,x:x+w]
            text = ocr(roi, language='jpn').strip()
            # #print out ocr result and contour info
            # print('stripped text:{}'.format(text.strip()))
            # print('stripped text length:{}'.format(len(text.strip())))
            # # print('area: {}'.format(cv2.contourArea(crop_c)))
            # print('area: {}'.format(w*h))
            # print('----------------------------------------------')

            #test
            # if True:
            #SECOND CONDITION: get the contour that matches:
            if is_question(text) or number_between_bracket(text):

                # cv2.rectangle(img, (x, y), (x + w, y + h), (36,255,12), 2) #draw box around contour

                if text == "問題 |":
                    text = "問題 1"

                if is_question(text):
                    if not bool(re.search(r'^問題[0-9]+$', text)):
                        text = clean_quesiton_name(text)
                if number_between_bracket(text):
                    if not bool(re.search(r'^\([0-9]+\)$', text)):
                        text = clean_bracket_name(text)

                # print out ocr result and contour info
                print('stripped text:{}'.format(text))
                print('stripped text length:{}'.format(len(text)))
                print('area: {}'.format(w * h))
                print('----------------------------------------------')

                #Determine 読解 or 聴解
                if text == '問題1':
                    section_count += 1
                #Determine 問題8
                if text == "問題8":
                    mondai8_count = 1
                    mondai9_count = 0
                    min_area = min_area_small
                # Determine 問題9
                if text == "問題9":
                    mondai9_count = 1
                    mondai8_count = 0
                    min_area = min_area_small

                if text == "問題10":
                    mondai9_count = 0
                    mondai8_count = 0
                    min_area = min_area_big

                # if the text is in mondai 8 or 9:
                if mondai8_count == 1 and mondai9_count == 0:
                    text = '問題8 ' + text
                elif mondai9_count == 1 and mondai8_count == 0:
                    text = '問題9 ' + text

                # Append 読解 or 聴解
                if section_count <= 1:
                    text = '文字読解 ' + text
                else:
                    text = '聴解 ' + text

                if text != "文字読解 問題8 問題8" and text != "文字読解 問題9 問題9":
                    line_items_coordinates.append([(x, y), (x + w, y + h)])  # save contour coordinate info
                    coordinates_name.append(text) #save contour text

    return line_items_coordinates, img, min_area, coordinates_name

def extract_mondai(img, save_folder_path, min_area, min_area_big, min_area_small, max_area, height_crop_rate,
                   width_crop_rate, show_img=True):

    global buffer_img
    global buffer_name
    global key

    #crop height
    img = resize_img(img, y0=floor(img.shape[0]*height_crop_rate), y1=floor(img.shape[0]*(1-height_crop_rate)))

    #crop width
    width_cropped_img = resize_img(img, x1=floor(img.shape[1]*width_crop_rate))

    cv2.imshow("hi", width_cropped_img)
    key = cv2.waitKey(0)

    #Recognize sections in the cropped page
    line_items_coordinates, roi_img, min_area, coordinates_name = ROI(width_cropped_img,min_area=min_area,
                                                                         min_area_small= min_area_small,
                                                                         min_area_big = min_area_big,
                                                                         max_area=max_area)

    for i in range(len(line_items_coordinates)):
        try:
            #handle the first section
            if i == 0:
                buffer_cut = resize_img(img, x0=0, x1=img.shape[1],
                             y0=0, y1=line_items_coordinates[i][0][1])
                if numpy.all(buffer_img == 255) and buffer_img.shape[0] == 1:
                    buffer_img = 255 * numpy.ones((1, buffer_cut.shape[1], 3), numpy.uint8)
                buffer_cut = cv2.vconcat([buffer_img, buffer_cut])
                if show_img == True:
                    cv2.imshow("img", buffer_cut)
                    key = cv2.waitKey(0)
                if buffer_name != "buffer img":
                    save_file_path = save_folder_path + '/' + buffer_name + '.jpg'
                    cv2.imwrite(save_file_path, buffer_cut)

            #handle middle section
            cut = resize_img(img, x0=0, x1=img.shape[1],
                             y0=line_items_coordinates[i][0][1], y1=line_items_coordinates[i+1][0][1])
            if show_img == True:
                cv2.imshow("img", cut)
                key = cv2.waitKey(0)
            save_file_path = save_folder_path + '/' + coordinates_name[i] + '.jpg'
            cv2.imwrite(save_file_path, cut)
        
        #handle last section
        except IndexError:
            cut = resize_img(img, 0, x1=img.shape[1],
                             y0=line_items_coordinates[i][0][1], y1=img.shape[0])
            buffer_img = cut
            buffer_name = coordinates_name[i]

    if len(line_items_coordinates) == 0:
        buffer_cut = resize_img(img, x0=0, x1=img.shape[1], y0=0, y1=img.shape[0])
        buffer_img = cv2.vconcat([buffer_img, buffer_cut])

    return min_area, buffer_img, buffer_name

@timeit
def main_program(path, save_path_base, min_area_small, min_area_big, max_area, height_crop_rate, width_crop_rate,
                 show_img=True):

    global key

    min_area = min_area_big

    path_file_name = os.path.splitext(os.path.basename(path))[0]
    save_folder_path = save_path_base + path_file_name

    #make the folder
    if not os.path.exists(save_folder_path):
        os.makedirs(save_folder_path)

    #convert pdf to image file
    pdf_imgs = convert_from_path(path)

    for img in pdf_imgs:
        img = convert_pil_to_cv2(img)
        min_area, buffer_img, buffer_name = extract_mondai(img, save_folder_path, min_area=min_area,
                                                           min_area_big = min_area_big,
                                                           min_area_small = min_area_small,
                                                           max_area=max_area,
                                                           height_crop_rate=height_crop_rate,
                                                           width_crop_rate=width_crop_rate,
                                                           show_img=show_img)
        if key == ord('q'):
            break

    #handle last imgage
    save_file_path = save_folder_path + '/' + buffer_name + '.jpg'
    cv2.imwrite(save_file_path, buffer_img)
    if show_img == True:
        cv2.imshow("img", buffer_img)
        key = cv2.waitKey(0)
        cv2.destroyAllWindows()

if __name__ == "__main__":

    #specify path of folder that contains pdf files
    pdf_folder_path = "/code_base/pdf_files/"

    #specify folder to save image files
    save_path_base = "/code_base/pdf_files/"

    #get list of pdf files name
    onlyfiles = [f for f in os.listdir(pdf_folder_path) if f.endswith('.pdf') and not f.endswith('Answer.pdf')]

    for f in onlyfiles:

        section_count = 0
        mondai8_count = 0
        mondai9_count = 0

        main_program(
            path=pdf_folder_path + f,
            save_path_base = save_path_base,
        min_area_big=2000, min_area_small=2000, max_area=10000, height_crop_rate=0.043, width_crop_rate=0.23, show_img=False)

        #min_area_big=3900, min_area_small=3200, max_area=4200, height_crop_rate=0.043, width_crop_rate=0.145, show_img=False
