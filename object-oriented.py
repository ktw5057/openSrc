from pre_json import preprocess_json_in_folder   #json [텍스트/x좌표/y좌표] 전처리 함수
from image_box import image_box_detect   #openCV로 표 박스 탐지 및 마우스 이벤트
from get_horizon_img import get_horizon_img
from get_json import get_json
from get_text_in_box import get_texts_in_boxes_for_folder
from excel_export import output_texts_to_excel
from json_preprocessor2 import preprocess_json

import json
import os
import requests

class Menu:
    def __init__(self):
        self.api_url = 'https://3hpzx86f4g.apigw.ntruss.com/custom/v1/21914/2b5953073d7c8d324205a0c0120809030a7117ac2a974b2b1538b87ffd78004d/general'
        self.secret_key = 'aVlTU3Vud29sR3pZakJXRE1Id2dNWlZycWd1TlFYWGE='
        self.bfe_img_path = "before_img" #원본 이미지 폴더
        self.aft_img_path = "after_img" #수평 맞춘 이미지 저장 폴더
        self.json_folder_path = "image_ocr_json" #OCR후 json이 저장될 폴더
        self.pre_json_folder_path = "preprocessed_json"
        self.output_excel_path = "xlsx"
        self.selected_boxes_info = None
        self.get_text_data = None
        self.json_file_path = None
        self.image_box_detect_path = None

    def get_horizon_image(self):
        get_horizon_img(self.bfe_img_path, self.aft_img_path)

    def start_ocr(self):
        get_json(self.aft_img_path, self.json_folder_path, self.api_url, self.secret_key)

    def preprocess_json_files(self):
        preprocess_json_in_folder(self.json_folder_path, self.pre_json_folder_path)

    def get_boxes_info(self):
        for jsonFile in os.listdir(self.json_folder_path):
            if jsonFile.endswith('.json'):
                self.json_file_path = os.path.join(self.json_folder_path, jsonFile)
                break

        for imgFile in os.listdir(self.aft_img_path):
            if imgFile.endswith('.png') or imgFile.endswith('.jpg') or imgFile.endswith('.PNG'):
                self.image_box_detect_path = os.path.join(self.aft_img_path, imgFile)
                break

        with open(self.json_file_path, 'r', encoding='utf-8') as json_file:
            json_data = json.load(json_file)

        preprocessed_data = preprocess_json(json_data)
        self.selected_boxes_info = image_box_detect(self.image_box_detect_path)

    def extract_text(self):
        if self.selected_boxes_info:
            self.get_text_data = get_texts_in_boxes_for_folder(self.selected_boxes_info, self.pre_json_folder_path)

    def convert_to_excel(self):
        if self.get_text_data:
            output_texts_to_excel(self.get_text_data, self.output_excel_path)

    def selectingData(self):
        self.get_horizon_image()
        self.start_ocr()
        self.preprocess_json_files()
        self.get_boxes_info()

    def Convert(self):
        self.extract_text()
        self.convert_to_excel()

if __name__ == "__main__":
    menu = Menu()

    while(1):
        active = int(input("하고싶은 기능의 번호를 입력하시오.\n 1. 시작 \n 2. 종료\n선택: "))
        if (active == 1):
            print("프로그램을 시작합니다.")
            print("추출하고 싶은 데이터 고르기")
            print("우클릭하면서 드래그하면 추출하고 싶은 데이터를 고르실 수 있습니다. / 고르신 데이중에 취소하고 싶으면 좌클릭 한번 누르시면 됩니다")
            print("빨간색 : 선택한 데이터 / 초록색 : 선택 안한 데이터")
            menu.selectingData()
            menu.Convert()
        if(active == 2):
            print("프로그램을 종료합니다.")
            break


