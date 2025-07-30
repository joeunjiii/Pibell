import os
import time
import threading
import requests
import cv2
from picamera import PiCamera
import RPi.GPIO as GPIO
from flask import Flask, Response

# 핀 설정
BUTTON_PIN = 21
MOTION_SENSOR_PIN = 14  # 모션 센서 핀 번호
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(MOTION_SENSOR_PIN, GPIO.IN)

# Pushover 앱 API 설정
PUSHOVER_USER_KEY = "uf24xs5hso67ncugyz57j6mpb21n1v"  # 사용자 키
PUSHOVER_API_TOKEN = "abchdfd4ra4ddh7a4jd7nfden92b84"  # API 토큰
PUSHOVER_URL = "https://api.pushover.net/1/messages.json"

# 카메라 설정
camera = PiCamera()
camera.resolution = (1024, 768)

# Flask 애플리케이션 설정
app = Flask(__name__)

# 타이머 상태
motion_timer = None
motion_detected_flag = False

@app.route('/stream')
def stream():
    """실시간 스트리밍"""
    def generate():
        camera.start_preview()
        time.sleep(2)  # 카메라 준비
        while True:
            camera.capture('/tmp/frame.jpg')
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + open('/tmp/frame.jpg', 'rb').read() + b'\r\n')
        camera.stop_preview()
    
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

def capture_photo(photo_path):
    """사진을 촬영하고 저장"""
    camera.start_preview()
    time.sleep(2)  # 카메라 준비
    camera.capture(photo_path)
    camera.stop_preview()
    print(f"사진 저장 확인: {photo_path}")

def detect_faces(photo_path):
    """얼굴 감지"""
    cascade_path = '/usr/local/share/opencv4/haarcascades/haarcascade_frontalface_default.xml'
    face_cascade = cv2.CascadeClassifier(cascade_path)
    image = cv2.imread(photo_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    print(f"감지된 얼굴 수: {len(faces)}")
    return len(faces) > 0  

def send_pushover_with_photo(photo_path):
    """Pushover 알림 전송 (사진 포함)"""
    with open(photo_path, "rb") as photo:
        files = {
            "token": (None, PUSHOVER_API_TOKEN),
            "user": (None, PUSHOVER_USER_KEY),
            "message": (None, "스마트 도어벨: 방문자를 확인하세요."),
            "attachment": ("photo.jpg", photo, "image/jpeg")
        }
        response = requests.post(PUSHOVER_URL, files=files)
        if response.status_code == 200:
            print("Pushover 알림 전송 완료")
        else:
            print(f"알림 전송 실패: {response.status_code}, {response.text}")

def motion_detected(channel):
    global motion_timer, motion_detected_flag
    print("모션이 감지되었습니다. 20초 타이머 시작...")
    motion_detected_flag = True

    # 기존 타이머가 실행 중이면 취소
    if motion_timer and motion_timer.is_alive():
        motion_timer.cancel()

    # 새 타이머 시작
    motion_timer = threading.Timer(20, send_alert_if_no_button_press)
    motion_timer.start()

    #모션센서 감지 후 0.5초동안 대기
    time.sleep(0.5)

def send_alert_if_no_button_press():
    global motion_detected_flag
    if motion_detected_flag:
        print("버튼이 눌리지 않았습니다. 알림 전송 시작...")
        send_streaming_url()
        motion_detected_flag = False

def button_pressed_callback(channel):
    global motion_timer, motion_detected_flag
    print("버튼이 눌렸습니다. 사진 촬영 시작...")
    motion_detected_flag = False

    # 타이머 취소
    if motion_timer and motion_timer.is_alive():
        motion_timer.cancel()

    # 사진 촬영 및 얼굴 인식
    photo_path = "/home/joeunji/smart_doorbell_photo.jpg"
    capture_photo(photo_path)
    if detect_faces(photo_path):
        send_pushover_with_photo(photo_path)
    else:
        print("얼굴이 감지되지 않았습니다. 알림을 전송하지 않습니다.")

def send_streaming_url():
    """실시간 스트리밍 URL을 Pushover로 전송"""
    streaming_url = "http://192.168.0.22:8000/stream"  # 스트리밍 URL 설정
    message = f"스마트 도어벨: 위험 알림! CCTV를 확인하세요! URL: {streaming_url}"
    files = {
        "token": (None, PUSHOVER_API_TOKEN),
        "user": (None, PUSHOVER_USER_KEY),
        "message": (None, message)
    }
    response = requests.post(PUSHOVER_URL, files=files)
    if response.status_code == 200:
        print("실시간 스트리밍 URL 전송 완료")
    else:
        print(f"알림 전송 실패: {response.status_code}, {response.text}")

# 버튼 및 모션 센서 이벤트 감지
GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING, callback=button_pressed_callback, bouncetime=500)
GPIO.add_event_detect(MOTION_SENSOR_PIN, GPIO.RISING, callback=motion_detected)

if __name__ == '__main__':
    # Flask 서버 시작
    from threading import Thread

    def run_flask_app():
        app.run(host='0.0.0.0', port=8000)

    thread = Thread(target=run_flask_app)
    thread.start()
    
    print("스마트 도어벨 시스템 준비 완료. 버튼을 눌러 실행하세요.")
    while True:
        time.sleep(1)