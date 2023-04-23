from flask import Flask, render_template, url_for, request, jsonify, Response
import PyPDF2
import io
import openai
import cv2
import platform
from gaze_tracking import GazeTracking

openai.api_key = "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"

app = Flask(__name__)

gaze = GazeTracking()
webcam = cv2.VideoCapture(0)
app = Flask(__name__)

def gen_frames():  
    while True:
        # We get a new frame from the webcam
        _, frame = webcam.read()

        # We send this frame to GazeTracking to analyze it
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
        cv2.putText(frame, "Left pupil:  " + str(left_pupil), (90, 130), cv2.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31), 1)
        cv2.putText(frame, "Right pupil: " + str(right_pupil), (90, 165), cv2.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31), 1)

        # cv2.imshow("Demo", frame)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result

        if cv2.waitKey(1) == 27:
            break

        #webcam.release()
    ##cv2.destroyAllWindows()

def makeRequest(messages):
    return openai.ChatCompletion.create(
                model = "gpt-3.5-turbo",
                messages = [messages]
            )

def makeQuestion(article):
    text = ""
    pd_text = []
    pd_text_row = []

    article = article.split(".")

    for text in range(len(article)):
        pd_text_row.append(article[text])

        if (text + 1) % 15 == 0:
            pd_text.append("".join(pd_text_row))
            pd_text_row = []

    result = ""

    print("텍스트를 gpt 녀석에게 요약시키고 있습니다.")
    print("긴 텍스트는 15문장을 기준으로 구분되어 gpt가 기억합니다.")

    #자기소개서 내용 요약. result에 요약한 내용 저장
    for i in range(len(pd_text)):
        currentText = pd_text[i]

        question = {"role":"user", "content": "다음 내용을 읽고 한국말로 요약해줘.\n" + currentText}
        completion = makeRequest(question)
        response = completion['choices'][0]['message']['content'].strip()
        result += response

        print(f"{i + 1}번째 텍스트를 gpt녀석이 기억했습니다.")
    
    question = {"role":"user", "content": "다음 글을 읽고 현재 면접 중이고 너가 면접관이라 생각하고 한국어 질문 세가지를 배열 형식으로 반환해줘\n" + result}

    print("gpt가 질문을 생성중입니다.")

    completion = makeRequest(question)

    response = completion['choices'][0]['message']['content'].strip()

    print(response)

    return response

@app.route('/')
def home():
    return render_template('index1.html')

@app.route('/video')
def index():
    return render_template('liveCam.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/interview')
def interview():
    return render_template('interview.html')

@app.route('/interviewResult')
def interviewResult():
    return render_template('interviewResult.html')
    
@app.route('/pdf', methods=['POST'])
def getPdfText():
    # 파일 읽기 시작
    print("파일을 읽고 있습니다")
    
    # js로 요청 넣은 파일을 가져온다.
    file = request.files['file']

    # PyPDF2 라이브러리의 PdfReader 메서드를 통해 파일을 읽는다.
    reader = PyPDF2.PdfReader(file)
    
    article = ''
    
    # 페이지 별로 읽어온 pdf 파일의 텍스트를 article 변수에 더해준다.
    for page_num in range(len(reader.pages)):
        page = reader.pages[page_num]
        article += page.extract_text()

    # 만든 전체 자소서 텍스트를 gpt에 넘겨 질문을 생성한다.
    question = makeQuestion(article)

    # 생성된 질문(string type array)을 questionArray라는 key값의 value로 설정한 dictionary를 만든다.
    # 만들어진 dictionary를 jsonify 메서드를 사용해 json형태로 변환한 후 반환해준다.
    return jsonify({"questionArray" : question})

@app.route('/test', methods=['GET'])
def getTest():
    return jsonify({"hi": "hihi"})


if __name__ == '__main__':
    #app.run('127.0.0.1', 5000, debug=True)
    app.run(debug=True)