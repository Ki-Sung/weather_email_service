# 날씨 알리미 서비스 (Weather Alert Service)
날씨 알리미는 매일 아침 서울의 날씨 정보를 이메일로 전송하는 서비스입니다. 비, 눈, 폭염, 한파 등 특별한 날씨 상황을 알려주고 대기 질 정보도 함께 제공합니다.

## 주요 기능
- 매일 아침 7시에 서울 지역 날씨 정보 이메일 전송
- 현재 날씨, 최고/최저 온도 정보 제공
- 대기질 정보 및 마스크 착용 권고 제공
- 계절별 특별 주의사항 (폭염, 한파)
- 날씨 상태별 맞춤 메시지
- 비/눈 예보 시 우산 챙기라는 알림
- 메모리 자동 최적화 및 로그 관리

## 프로젝트 구조
```
app/
│
├── config/
│   └── settings.py       # 설정 및 환경 변수
│
├── services/
│   ├── weather_service.py     # 날씨 데이터 관련 함수
│   └── email_service.py       # 이메일 전송 관련 함수
│
├── utils/
│   └── helpers.py        # 유틸리티 함수 및 헬퍼 클래스
│
├── .env                  # 환경 변수 파일 (비공개)
├── main.py               # 애플리케이션 진입점
├── requirements.txt      # 필요한 패키지 목록
└── README.md             # 프로젝트 설명
```

## 설치 방법

### 1. 저장소 복제
```bash
git clone https://github.com/사용자명/weather-mail.git
cd weather-mail
```

### 2. 가상 환경 설정 (권장)
```bash
# 가상 환경 생성
python -m venv venv

# 가상 환경 활성화 (Windows)
venv\Scripts\activate

# 가상 환경 활성화 (macOS/Linux)
source venv/bin/activate
```

### 3. 필요한 패키지 설치
```bash
pip install -r requirements.txt
```

## 환경 변수 설정
프로젝트 루트 디렉토리에 `.env` 파일을 생성하고 다음 환경 변수를 설정하세요:

```ini
# OpenWeatherMap API 키
OWM_API_KEY=your_openweathermap_api_key

# 이메일 서버 설정
SMTP_HOST="smtp.your-email-provider.com"
SMTP_PORT=25
SMTP_USER="your_email@example.com"
SMTP_PASSWORD="your_email_password"
SMTP_FROM="your_email@example.com"

# 수신자 설정
RECIPIENT="main_recipient@example.com"
BCC_RECIPIENTS=["hidden_recipient1@example.com", "hidden_recipient2@example.com"]
```

### OpenWeatherMap API 키 얻기
1. [OpenWeatherMap](https://openweathermap.org/)에 가입하세요.
2. 로그인 후 My API Keys 섹션에서 새 API 키를 생성하세요.
3. 생성한 API 키를 `.env` 파일의 `OWM_API_KEY` 변수에 입력하세요.

## 실행 방법

### 일반 실행 (스케줄러 모드)
이 모드는 매일 아침 7시에 날씨 이메일을 자동으로 전송합니다.

```bash
python main.py
```

### 테스트 모드 (즉시 실행)

환경 설정을 테스트하기 위해 즉시 날씨 이메일을 전송합니다.

```bash
python main.py --now
```

### 백그라운드 실행 (Linux/macOS)
nohup을 사용하여 백그라운드에서 실행할 수 있습니다:

```bash
nohup python main.py > nohup.out 2>&1 &
```

### 서비스로 등록 (Linux)
systemd를 사용하여 서비스로 등록하려면 다음과 같이 서비스 파일을 생성하세요:

```bash
sudo nano /etc/systemd/system/weather-mail.service
```

다음 내용을 입력하세요 (경로를 실제 설치 경로로 수정하세요):

```ini
[Unit]
Description=Weather Mail Service
After=network.target

[Service]
User=your_username
WorkingDirectory=/path/to/weather_mail
ExecStart=/path/to/weather_mail/venv/bin/python /path/to/weather_mail/main.py
Restart=on-failure
RestartSec=10
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=weather-mail

[Install]
WantedBy=multi-user.target
```

서비스 활성화 및 시작:

```bash
sudo systemctl daemon-reload
sudo systemctl enable weather-mail
sudo systemctl start weather-mail
```

## 이메일 내용 설명
서비스에서 전송하는 이메일은 다음 정보를 포함합니다:

1. **현재 날씨 상태**: 맑음, 비, 눈 등 현재 날씨 상태와 아이콘
2. **온도 정보**: 현재 온도, 최고 온도, 최저 온도
3. **대기질 정보**: 대기질 수준(좋음, 보통, 나쁨 등)과 마스크 착용 권고 여부
4. **특별 알림**: 
   - 여름철(6-8월) 최고 온도 33℃ 이상: 폭염 주의 메시지
   - 겨울철(12-2월) 최저 온도 -12℃ 이하: 한파 주의 메시지
   - 비/눈 예보 시 - 해당 예보시 우산을 챙겨라 라는 메시지
       - 소나기 예보
       - 천둥번개 동반한 장대비 예보
       - 일반 비 예보
       - 눈 예보

## 커스터마이징

### 위치 변경
다른 도시의 날씨 정보를 받고 싶다면 `config/settings.py` 파일에서 위도와 경도 값을 수정하세요:

```python
# 위치 좌표 설정 (예: 부산)
SEOUL_LAT = 35.1796
SEOUL_LON = 129.0756
```

### 스케줄 시간 변경
이메일 전송 시간을 변경하려면 `config/settings.py` 파일에서 다음을 수정하세요:

```python
# 스케줄 설정 (예: 오후 6시)
SCHEDULE_TIME = "18:00"
```

## 문제 해결

### 이메일이 전송되지 않는 경우
1. `.env` 파일의 SMTP 설정이 올바른지 확인하세요.
2. 이메일 서비스 제공자의 보안 설정을 확인하세요. 일부 서비스는 보안 수준이 낮은 앱의 접근을 차단할 수 있습니다.
3. 로그 파일(`weather_mail.log`)을 확인하여 오류 메시지를 확인하세요.

### 날씨 데이터를 가져오지 못하는 경우
1. OpenWeatherMap API 키가 유효한지 확인하세요.
2. 인터넷 연결 상태를 확인하세요.
3. API 요청 할당량을 초과했는지 확인하세요.

## 라이센스
이 프로젝트는 MIT 라이센스에 따라 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 기여하기
1. 이 저장소를 포크합니다.
2. 새 기능 브랜치를 생성합니다 (`git checkout -b feature/amazing-feature`).
3. 변경 사항을 커밋합니다 (`git commit -m 'Add some amazing feature'`).
4. 브랜치에 푸시합니다 (`git push origin feature/amazing-feature`).
5. Pull Request를 생성합니다.

---
날씨 알리미 서비스를 사용해 주셔서 감사합니다! 질문이나 피드백이 있으시면 이슈를 등록해 주세요.
