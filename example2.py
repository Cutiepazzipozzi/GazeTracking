from flask import Flask, Response, render_template
import cv2
import platform
from gaze_tracking import GazeTracking
import time as Time

gaze = GazeTracking()
webcam = cv2.VideoCapture(0)
 
count = 0
firstLeft = []
firstRight = []
fault = 0
# time = 0 (초 단위로 눈 움직임을 체크할 때 쓰려했으나, 전체 초와 전체 움직임을 계산할것이므로 일단 주석 처리함)
# 1프레임 = 0.06~0.08초 => 대략 15프레임당 1초, 15프레임때만 체크
# 1초당 7번 정도의 움직임이면 좀 심각한듯..?
# 1초당 2번~3번 정도의 움직임이 평균일 거 같음
# 1초당 0번~1번 정도의 움직임이면 좋은 거 같음
while True:
        if(count == 0): start = Time.time()
        # We get a new frame from the webcam
        _, frame = webcam.read()

        # We send this frameto GazeTracking to analyze it
        gaze.refresh(frame)

        frame = gaze.annotated_frame()
        text = ""

        if gaze.is_blinking():
            text = "Blinking"
        elif gaze.is_right():
            text = "Looking right"
        elif gaze.is_left():
            text = "Looking left"
        elif gaze.is_center():
            text = "Looking center"

        cv2.putText(frame, text, (90, 60), cv2.FONT_HERSHEY_DUPLEX, 1.6, (147, 58, 31), 2)

        left_pupil = gaze.pupil_left_coords()
        right_pupil = gaze.pupil_right_coords()

        if count == 0: 
            print(f"처음 시선 왼쪽 눈동자: {left_pupil} 오른쪽 눈동자: {right_pupil}")
            firstLeft = left_pupil
            firstRight = right_pupil
            count += 1
        
        if type(left_pupil) != type(None) and type(right_pupil) != type(None):
            if abs(sum(firstLeft)-sum(left_pupil)) >= 7 or abs(sum(firstRight)-sum(right_pupil) >= 7) :
                cv2.putText(frame, "Please look straight to the screen", (90, 105), cv2.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31), 1)
                fault += 1

        cv2.putText(frame, "Left pupil:  " + str(left_pupil), (90, 130), cv2.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31), 1)
        cv2.putText(frame, "Right pupil: " + str(right_pupil), (90, 165), cv2.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31), 1)

        cv2.imshow("Demo", frame)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
       
        if cv2.waitKey(1) == 27:
            break
        
        print(fault)

        end = Time.time()
        print(end-start)

webcam.release()
cv2.destroyAllWindows()