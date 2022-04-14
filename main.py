import base64
import requests
import json
import os
import pandas as pd
from tqdm import tqdm

url = "http://192.168.0.199:5000/api/v1/detect-liveness"
models = ['fasnet', 'FTNet', 'default', 'rose_full_374']
images_path = '/home/myid/test/test_individual_models/'
# images_path = '/Users/yoshlikmedia/Projects/test_individual_model/'
df = pd.DataFrame()
folders = ['AA3642573/', 'AA4469267/', 'AC2155899/']

def base64_encode(image_path):
    """
    Encode images Data URI - data:contenttype;base64,encoded_string
    :param image_path:
    :return:
    """
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
        encoded_string = encoded_string.decode("utf-8")
        encoded_string = "data:image/png;base64," + encoded_string
        return encoded_string


single_face_only = True
with_filter = True
open_eyes_only = True
color_image_only = False
headers = {'Content-Type': 'application/json'}

for folder in folders:
    images = [f for f in os.listdir(images_path + folder) if f.endswith('.jpeg')]
    images = os.listdir(images_path + folder)
    print(images)

    for image in tqdm(images):
        model_ans = {}
        model_ans_blur = []
        image_path = images_path + folder + image
        encoded_string = base64_encode(image_path)

        for model in tqdm(models):
            payload = json.dumps({
                "model": "{}".format(model),
                "single_face_only": single_face_only,
                "with_filter": True,
                "open_eyes_only": open_eyes_only,
                "color_image_only": color_image_only,
                "image_b64": "{}".format(encoded_string)
            })

            response = requests.request("POST", url, headers=headers, data=payload)
            try:
                result = response.json()['liveness_result']       
                model_ans[model] = result['is_real']
            except Exception as ex:
                try:
                    model_ans[model] = response.json()['detail']
                except Exception as ex:
                    print(ex)

            blur_payload = json.dumps({
                "model": "{}".format(model),
                "single_face_only": single_face_only,
                "with_filter": False,
                "open_eyes_only": open_eyes_only,
                "color_image_only": color_image_only,
                "image_b64": "{}".format(encoded_string)
            })

            blur_response = requests.request("POST", url, headers=headers, data=blur_payload)
            try:
                blur_result = blur_response.json()['liveness_result']       
                model_ans_blur[model] = blur_result['is_real']
            except Exception as ex:
                try:
                    model_ans_blur[model] = response.json()['detail']
                except Exception as ex:
                    print(ex)
        try: 
            data = {
                'image': image,
                'fasnet': model_ans['fasnet'],
                'FTNet': model_ans['FTNet'],
                'default': model_ans['default'],
                'rose_full_374': model_ans['rose_full_374'],
                'blur-fasnet': model_ans_blur['fasnet'],
                'blur-FTNet': model_ans_blur['FTNet'],
                'blur-default': model_ans_blur['default'],
                'blur-rose_full_374': model_ans_blur['rose_full_374'],
            }   

            df = df.append(data, ignore_index=True)
            print(df)
        except Exception as ex:
            print(ex)
        
    # print(f'{images_path + folder[:-1]}/{folder[:-1]}.xlsx')
    df.to_excel(f'{images_path + folder[:-1]}/{folder[:-1]}.xlsx')
    df = pd.DataFrame()
