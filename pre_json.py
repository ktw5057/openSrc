import os
import json
# json파일에서 단어, 단어의 좌표를 추출하고 그것을 리스트에 저장한다음 저장시킬 파일에 그 리스트 내용을 저장한다
def preprocess_json_in_folder(json_folder_path, output_folder_path):# json파일이 있는 폴더의 경로,이함수 결과가 어디폴더의 경로에 저장될건지 인수로 받는다
    processed_data = []
    for json_file in os.listdir(json_folder_path): #json_folder_path경로의 파일에 있는 파일목록의 요소들을 json_file라는 변수에 하나하나씩 넣어본다
        if json_file.endswith('.json'): #json_file이 .json으로 끝나면 다음코드 실행 아니면 바로 맨끝에 있는 print문으로 감
            with open(os.path.join(json_folder_path, json_file), 'r', encoding='utf-8') as f: #json_folder_path와 json_file(파일이름)을 합치고 파일주소를 f에 할당 그 경로로 파일을 읽기전용으로 파일객체를 생성하고 with open안의 코드 끝나면 파일을 닫는다
                json_data = json.load(f) # f를 인수로 줘서 f에 있는 json문자열을 파이선의 딕트나 리스트로 변환시킴 디코딩
                for image in json_data['images']:
                    for field in image['fields']:
                        text = field['inferText']
                        vertices = field['boundingPoly']['vertices'] # 인식된 단어의 좌표 상단 좌우 하단 좌우 4개의 자표를 vertices에 리스트형식으로줌
                        x_coordinates = [vertex['x'] for vertex in vertices]  #단어의 x의 값들을 모두 넣는다 리스트
                        y_coordinates = [vertex['y'] for vertex in vertices]  #단어의 y의 값들을 모두 넣는다 리스트
                        processed_data.append([text, x_coordinates, y_coordinates]) # processed_data에 단어 , x좌표 값들  ,y 좌표 값들
                
            # 전처리된 데이터를 JSON 형식으로 저장
            output_file_path = os.path.join(output_folder_path, f"{os.path.splitext(json_file)[0]}_processed.json")  #저장시킬폴더 즉 디렉터리 경로와 os.path.splitext(json_file)을 써서 파일이름과 확장자를 분리한다음 파일이름만 _processed.json를 뒤에 붙여서 디렉토리 경로랑 합친다.
            with open(output_file_path, 'w', encoding='utf-8') as output_file: #저장시키고싶은 폴더를 연다 만약 해당 경로에 폴더가없으면 만들고 쓰기모드로 그파일을 객체 생성하고 그객체의 주소를 output_file이라는 변수에 저장한다.
                json.dump(processed_data, output_file) #processed_data를 json문자열로 인코딩함 그리고 output_file에 그내용을 저장시킴
            processed_data = []  # 리스트를 비워줍니다.

    print(f"Preprocessing is completed. Processed files are saved in {output_folder_path}")
