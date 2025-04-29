## 애플리케이션 설정 및 환경 변수
import os
from dotenv import load_dotenv

# 환경 변수 로드 
load_dotenv(verbose=True)

# 이메일 설정 
SMTP_HOST = os.getenv("SMTP_HOST")                   # SMTP 서버 주소
SMTP_PORT = os.getenv("SMTP_PORT")                   # SMTP 포트 번호   
SMTP_USER = os.getenv("SMTP_USER")                   # SMTP 사용자 이름 (이메일 주소)
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")           # SMTP 비밀번호
SMTP_FROM = os.getenv("SMTP_FROM")                   # 보내는 이메일 주소
RECIPIENT = os.getenv("RECIPIENT")                   # 수신자 이메일 주소

# BCC 수신자(추가 수신자) 처리 - 쉼표로 구분된 문자열을 리스트로 변환
BCC_RECIPIENTS_STR = os.getenv("BCC_RECIPIENTS", "")
BCC_RECIPIENTS = [email.strip() for email in BCC_RECIPIENTS_STR.split(",")] if BCC_RECIPIENTS_STR else []

# OpenWeatherMap API 설정
OWM_API_KEY = os.getenv("OWM_API_KEY")                                              # OpenWeatherMap API 키    
OWM_ENDPOINT = "https://api.openweathermap.org/data/3.0/onecall"                    # OpenWeatherMap API 엔드포인트
AIR_POLLUTION_ENDPOINT = "http://api.openweathermap.org/data/2.5/air_pollution"     # 대기질 API 엔드포인트

# 특징 지역 위도 경도 값 설정 - 지역: 서울
SEOUL_LAT = 37.541
SEOUL_LON = 126.986

# 스케줄 설정
SCHEDULE_TIME = "07:00"  # 매일 아침 7시