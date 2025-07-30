
# 📷 스마트 도어벨 프로젝트 - **Pibell**

## 📅 프로젝트 기간
2024년 11월 ~ 2024년 12월(총 3주)

## 🛠 프로젝트 개요
**Pibell**은 라즈베리파이와 PiCamera, 모션 센서, 버튼 등을 활용해 **실시간 스트리밍, 얼굴 인식, 알림 전송** 기능을 구현한 스마트 도어벨 시스템입니다.

## 🙋‍♂️ 담당 역할
- 모션센서를 활용한 실시간 스트리밍 기능 구현
- PiCamera + Notification App 기반 얼굴 인식 및 사진 촬영 기능 개발

---

## ⚙ 사용 부품 및 구성
- Raspberry Pi 4 (Legacy Version)
- Pi Camera 모듈
- PIR 모션 감지 센서
- 푸시 알림용 버튼
- 브레드보드 및 점퍼 와이어
- 
---

### 전체 회로도
<img width="833" height="738" alt="그림01" src="https://github.com/user-attachments/assets/8c7e5d2f-b68a-40df-b393-6e6c8de8c9cd" />

---


## 📦 환경 세팅 및 사전 준비

### 1. GPU 메모리 설정
```bash
sudo raspi-config
# → Performance Options → GPU Memory → 128MB 설정
```

### 2. swap size 변경
```bash
sudo nano /etc/dphys-swapfile
# CONF_SWAPSIZE=2048 로 수정
sudo /etc/init.d/dphys-swapfile restart
```

### 3. 필수 패키지 설치
```bash
sudo apt update
sudo apt install python3-opencv
pip3 install opencv-contrib-python
```

### 4. Numpy 다운그레이드
```bash
pip3 install numpy==1.24.2
```

### 5. Pushover 설정
- [Pushover API](https://pushover.net/) 토큰 발급 필요
- 사용자 및 앱 토큰 등록

### 6. Flask 서버 세팅
- `streaming_url`은 라즈베리파이의 IP 주소로 설정
- 포트 번호는 클라이언트/서버 일치 필수

---

## 🔑 주요 기능

| 기능 | 설명 |
|------|------|
| 얼굴 인식 | Haar-Cascade를 활용하여 방문자 얼굴 인식 및 자동 촬영 |
| 알림 전송 | 촬영된 사진과 함께 Pushover 앱으로 알림 전송 |
| 실시간 스트리밍 | Flask 서버를 통해 웹 브라우저로 실시간 카메라 영상 출력 |
| 모션 감지 | PIR 센서로 움직임 감지 시 자동 녹화 또는 알림 트리거 |

---

## 💡 추가 개발 아이디어
- 얼굴 DB 등록 및 허용 사용자만 알림 전송
- 음성 인터폰 기능 추가
- 클라우드 연동 자동 백업
