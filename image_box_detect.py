import cv2
import numpy as np
from combine_texts import combine_texts         #글자 결합 함수

def image_box_detect(image_path, preprocessed_data):
    
    img_array = np.fromfile(image_path, np.uint8) # 이미지파일에서 바이트데이터를 읽어와 Numpy배열로 변환 / np.uint8는 부호 없는 정수 타입이다 -> 이미지파일는 픽셀값(0~255)을 표현하는 숫자들의 집합이고 부호없는 정수로 표현된다.
    image = cv2.imdecode(img_array, cv2.IMREAD_COLOR) # numpy배열로 전환된 이미지를 인수로주고 cv2.IMREAD_COLOR로 컬러로 만들라는 인수를 준다. 그러면 numpy배열로 표현된 이미지를 컬러형식으로 바꾼다
    image_copy = image.copy()  # 원본 이미지 복사

    gray_scale=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY) # BRG형식 image를 그레이스케일 이미지로 변환함 (0~255 흑백명암)
    th1,img_bin = cv2.threshold(gray_scale,150,225,cv2.THRESH_BINARY) #영역분리 물체감지 경계검출을 위해 그레이스 스케일 이미지를 이진화한다  150이 임계값이고 150보다 작으면 0(검은색) 크면 225(흰색)이다.
    img_bin=~img_bin #이미지 색상을 반전시킨다  0->225  225->0
    #원본이미지  byte -> numpy배열  ->

    ### selecting min size as 15 pixels
    line_min_width = 15
    kernal_h = np.ones((1,line_min_width), np.uint8) # (1(행개수),15(열개수)) [1,1,1,1,1,.....] 부호없는 정수타입으로
    kernal_v = np.ones((line_min_width,1), np.uint8) # (15(행개수),1(열개수)) 부호없는 정수타입으로

    img_bin_h = cv2.morphologyEx(img_bin, cv2.MORPH_OPEN, kernal_h) #img_bin(색상반전된 이진화된 흑백 이미지)를 모폴로지연산을 함 cv2.MORPH_OPEN은 열림연산 kernal_h는 열림 연산에 사용되는 커널
    #열림연산 침식 (가장작은 값을 픽셀로 한다 -> 검은색이 많아짐 -> 작은 객체나 세부구조 사라짐)-> 팽창(가장큰값을 픽셀로한다  밝은색영역이 확대되고 구멍을 매꿈)
    #커널은 작을수록 작은 개체를 감지하기 쉽고 클수록 큰 개체를 감지하기 쉽다. 커널 구조가 (1,15)로 설정한이유는 가로방향 구조를 감지하기 위해서이다.
    img_bin_v = cv2.morphologyEx(img_bin, cv2.MORPH_OPEN, kernal_v) #위에꺼랑 비슷한 내용이다 커널방향만 세로방향 구조를 감지하기 위한거고

    img_bin_final=img_bin_h|img_bin_v  # OR연산이다 어쩌피 이진화 되어있으므로 가로 세로 검출한부분이 만난다하더라도 똑같은 값이므로 겹치는 부분은 상관없다.

    final_kernel = np.ones((3,3), np.uint8) #1로채워진 (3x3)인 numpy 2차원 배열
    img_bin_final=cv2.dilate(img_bin_final,final_kernel,iterations=1) #팽창연산 밝은 부분 확장시킨다 1번 전체 이미지 이진값들을 훑고 지나간다.

    #열림연산을 수평 수직 -> 하고 그걸 합치고 다시 팽창연산을 한다.

    _, labels, stats,_ = cv2.connectedComponentsWithStats(~img_bin_final, connectivity=8, ltype=cv2.CV_32S)#이진 이미지에서 객체의 연결 요소를 찾고, 각 연결 요소의 통계 정보를 추출하는 작업

    rectangles = []
    # cv2.connectedComponentsWithStats() 함수를 사용하면, stats 배열의 첫 번째 요소는 배경을 나타내는 정보를 포함 두번째부터 실제 객체이므로 stat두번째요소부터
    for x, y, w, h, _ in stats[2:]:
        cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2) #이미지에 녹색(0,255,0)으로 사각형을그린다 테두리 두께 2로
        rectangles.append([(x, x+w, x+w, x), (y, y, y+h, y+h)])  # 좌표 순서 변경

    selected = [False]*len(rectangles)  # 각 사각형의 선택 상태를 저장하는 리스트

    def click_and_crop(event, x, y, flags, param):
        # 마우스 왼쪽 버튼이 클릭되었을 때
        if event == cv2.EVENT_LBUTTONDOWN: #cv2.EVENT_LBUTTONDOWN 왼쪽 버튼이 눌렀느냐의 상수
            for idx, rect in enumerate(rectangles):
                (x1, x2, x3, x4), (y1, y2, y3, y4) = rect
                if x1 <= x <= x2 and y1 <= y <= y3:  # 클릭된 좌표가 사각형 내부에 있는 경우
                    selected[idx] = not selected[idx]  # 만약 선택상태가 False였으면 True 바꾸고 True이면 False로 바꾼다.
                    color = (0, 0, 255) if selected[idx] else (0, 255, 0)  # 선택되었다면 빨간색, 아니면 초록색
                    cv2.rectangle(image, (x1, y1), (x2, y3), color, 2)  # 사각형 색 변경

                    texts_in_box = []
                    for text, x_coordinates, y_coordinates in preprocessed_data:
                        center_x = sum(x_coordinates) / len(x_coordinates)
                        center_y = sum(y_coordinates) / len(y_coordinates)

                        # 텍스트의 중심 좌표가 선택된 박스 안에 있는지 확인합니다.
                        if x1 <= center_x <= x2 and y1 <= center_y <= y3:
                            texts_in_box.append([text, x_coordinates, y_coordinates])

                    combined_text = combine_texts(texts_in_box)
                    print(f'Text within selected box {idx+1}: {combined_text}')

                    cv2.imshow('detect', image)
                    break
                    

    cv2.namedWindow('detect')
    cv2.setMouseCallback('detect', click_and_crop)

    cv2.imshow('detect', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

