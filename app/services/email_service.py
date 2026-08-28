## 이메일 전송 관련 서비스
import logging
import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional, List, Tuple, Counter as CounterType
from collections import Counter
from datetime import datetime

from config.settings import (
    SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, SMTP_FROM, 
    RECIPIENT, BCC_RECIPIENTS
)
from config.settings import FORECAST_START_HOUR, FORECAST_HOURS
from utils.helpers import (
    get_weather_condition, 
    get_air_quality_level, 
    get_season_advice, 
    get_weather_message,
    analyze_humidity,
    get_optimal_humidity_range,
    get_humidity_condition,
    get_hourly_forecast_from_kst,
    to_kst,
    KST,
)

# 이메일 내용 생성 
def create_email_content(
    weather_data: Dict[str, Any], 
    air_quality_data: Optional[Dict[str, Any]]
) -> Dict[str, str]:
    """
    날씨 데이터를 기반으로 이메일 내용을 생성합니다.
    
    Args:
        weather_data (Dict[str, Any]): 날씨 정보가 포함된 JSON 객체
        air_quality_data (Optional[Dict[str, Any]]): 대기 질 정보가 포함된 JSON 객체 (없을 수 있음)
    
    Returns:
        Dict[str, str]: 이메일 제목과 본문 내용
    """
    # 날씨 정보가 없으면 오류 메시지 반환 
    if not weather_data:
        return {
            "subject": "[날씨 알리미] 날씨 정보 불러오기 실패",
            "body": "<p>날씨 정보를 불러오는 데 실패했습니다. 다시 시도해주세요.</p>"
        }
    
    # 현재 날씨 정보 추출
    current = weather_data.get("current", {})       # 현재 날씨 정보 
    hourly = get_hourly_forecast_from_kst(
        weather_data.get("hourly", []),
        start_hour=FORECAST_START_HOUR,
        count=FORECAST_HOURS,
    )
    daily = weather_data.get("daily", [])[0] if weather_data.get("daily") else {}    # 일일 데이터 
    
    # 필요한 데이터 추출
    current_temp = current.get("temp", 0)            # 현재 온도 
    temp_max = daily.get("temp", {}).get("max", 0) if daily else 0    # 최고 온도 
    temp_min = daily.get("temp", {}).get("min", 0) if daily else 0    # 최저 온도 
    
    # 현재 날씨 상태 추출
    current_weather = current.get("weather", [{}])[0]       # 현재 날씨 상태 
    current_weather_id = current_weather.get("id", 800)     # 날씨 아이디 
    
    # 15시간 동안의 주요 날씨 상태 파악
    overall_weather_condition, overall_weather_icon = get_overall_weather(hourly)
    
    # 대기질 정보
    air_quality_msg = "대기질 정보를 불러올 수 없습니다."
    air_quality_level = ""
    
    if air_quality_data and "list" in air_quality_data and air_quality_data["list"]:  # 대기질 데이터가 있고, 목록이 있으면 
        aqi = air_quality_data["list"][0].get("main", {}).get("aqi", 0)               # 대기질 지수 추출 
        # 대기질 지수가 있으면 대기질 수준 추출 
        if aqi:
            air_quality_level, air_quality_msg = get_air_quality_level(aqi)           # 대기질 수준과 메시지 추출 
    
    # 날씨 상태 확인
    current_condition, current_icon = get_weather_condition(current_weather_id)       # 현재 날씨 상태와 아이콘 추출 
    weather_msg = get_weather_message(overall_weather_condition)                      # 날씨 메시지 추출 (종합 날씨 기준)
    
    # 비 또는 눈 예보 확인 - 분리하여 확인
    will_rain, will_snow, will_shower, will_heavy_rain = check_precipitation_forecast(hourly)
    
    # 계절별 조언
    season_advice = get_season_advice(temp_max, temp_min)
    
    # 15시간 예보 HTML 생성
    hourly_forecast_html = generate_hourly_forecast_html(hourly)
    
    # 습도 분석
    humidity_data = analyze_humidity(hourly)
    morning_humidity = humidity_data["morning_avg"]
    afternoon_humidity = humidity_data["afternoon_avg"]
    overall_humidity = humidity_data["overall_avg"]
    
    # 현재 월 추출
    current_month = datetime.now(KST).month
    
    # 적정 습도 범위 계산 (아침/오후 각각)
    morning_min_optimal, morning_max_optimal = get_optimal_humidity_range(temp_min, current_month)
    afternoon_min_optimal, afternoon_max_optimal = get_optimal_humidity_range(temp_max, current_month)
    
    # 습도 상태 및 메시지 
    morning_humidity_condition, morning_humidity_icon, morning_humidity_msg = get_humidity_condition(
        morning_humidity, morning_min_optimal, morning_max_optimal
    )
    
    afternoon_humidity_condition, afternoon_humidity_icon, afternoon_humidity_msg = get_humidity_condition(
        afternoon_humidity, afternoon_min_optimal, afternoon_max_optimal
    )
    
    # 습도 정보 HTML 생성
    humidity_html = generate_humidity_html(
        morning_humidity, afternoon_humidity, overall_humidity,
        morning_humidity_condition, morning_humidity_icon, morning_humidity_msg,
        afternoon_humidity_condition, afternoon_humidity_icon, afternoon_humidity_msg
    )
    
    # 이메일 본문 작성
    msg_text = f"""
    <html>
    <body>
    <h2>오늘의 날씨 알림 {overall_weather_icon}</h2>
    
    <p>안녕하세요!</p>
    
    <p>오늘 서울의 날씨를 알려드립니다.</p>
    <hr>
    
    <h3>오늘의 종합 날씨: {overall_weather_condition} {overall_weather_icon}</h3>
    
    <p>{weather_msg}</p>
    
    <p>• 현재 온도: {current_temp:.1f}°C</p>
    
    <p>• 최고 온도: {temp_max:.1f}°C</p>
    
    <p>• 최저 온도: {temp_min:.1f}°C</p>
    <hr>
    
    <h3>습도 정보 💧</h3>
    {humidity_html}
    <hr>
    
    <h3>15시간 예보</h3>
    {hourly_forecast_html}
    <hr>
    
    <h3>대기질 정보: {air_quality_level}</h3>
    
    <p>{air_quality_msg}</p>
    <hr>
    """
    
    # 특별 알림 추가
    if season_advice:
        msg_text += f"<h3>특별 알림</h3>\n\n<p>{season_advice}</p>\n<hr>\n"
    
    # 소나기 예보 확인
    if will_shower:
        msg_text += "<p><strong>🌦️ 오늘 소나기가 예상됩니다! 갑작스러운 날씨 변화에 대비하세요.</strong></p>\n<hr>\n"
    
    # 강한 비 예보 확인
    elif will_heavy_rain:
        msg_text += "<p><strong>🌧️ 오늘 강한 비가 예상됩니다! 외출을 자제하고 우산을 꼭 챙기세요.</strong></p>\n<hr>\n"
    
    # 일반 비 예보 확인
    elif will_rain:
        msg_text += "<p><strong>☔ 오늘 비가 예상되니 외출 시 우산을 꼭 챙기세요!</strong></p>\n<hr>\n"
    
    # 눈 예보 확인
    if will_snow:
        msg_text += "<p><strong>❄️ 오늘 눈이 예상되니 외출 시 따뜻하게 입고 미끄럼에 주의하세요!</strong></p>\n<hr>\n"
    
    # 이메일 본문 추가 
    msg_text += """
    <p>좋은 하루 되세요!</p>
    
    <p>날씨 알리미 드림</p>
    </body>
    </html>
    """
    
    # 제목 설정 - 날씨 유형별 세분화
    subject = f"[날씨 알리미] 오늘의 날씨: {overall_weather_condition} {overall_weather_icon}"
    
    if will_shower and will_snow:
        subject = f"[날씨 알리미] 오늘 소나기와 눈 예보! 갑작스러운 날씨 변화에 대비하세요 {overall_weather_icon}"
    elif will_shower:
        subject = f"[날씨 알리미] 오늘 소나기 예보! 갑작스러운 날씨 변화에 대비하세요 {overall_weather_icon}"
    elif will_heavy_rain and will_snow:
        subject = f"[날씨 알리미] 오늘 강한 비와 눈 예보! 외출을 자제하세요 {overall_weather_icon}"
    elif will_heavy_rain:
        subject = f"[날씨 알리미] 오늘 강한 비 예보! 외출을 자제하고 우산을 챙기세요 {overall_weather_icon}"
    elif will_rain and will_snow:
        subject = f"[날씨 알리미] 오늘 비와 눈 예보! 우산을 챙기세요 {overall_weather_icon}"
    elif will_rain:
        subject = f"[날씨 알리미] 오늘 비 예보! 우산을 챙기세요 {overall_weather_icon}"
    elif will_snow:
        subject = f"[날씨 알리미] 오늘 눈 예보! 따뜻하게 입으세요 {overall_weather_icon}"
    
    return {
        "subject": subject,
        "body": msg_text
    }


def generate_humidity_html(
    morning_humidity: float, 
    afternoon_humidity: float, 
    overall_humidity: float,
    morning_condition: str, 
    morning_icon: str, 
    morning_msg: str,
    afternoon_condition: str, 
    afternoon_icon: str, 
    afternoon_msg: str
) -> str:
    """
    습도 정보를 HTML 형식으로 생성합니다.
    
    Args:
        morning_humidity: 오전 평균 습도
        afternoon_humidity: 오후 평균 습도
        overall_humidity: 전체 평균 습도
        morning_condition: 오전 습도 상태
        morning_icon: 오전 습도 아이콘
        morning_msg: 오전 습도 메시지
        afternoon_condition: 오후 습도 상태
        afternoon_icon: 오후 습도 아이콘
        afternoon_msg: 오후 습도 메시지
        
    Returns:
        str: HTML 형식의 습도 정보
    """
    html = f"""
    <div style="margin-bottom: 15px;">
        <table style="width:100%; border-collapse: collapse; margin-bottom: 15px;">
            <tr style="background-color: #e6f7ff;">
                <th style="padding: 8px; border: 1px solid #ddd; width: 33%;">오전 평균 습도</th>
                <th style="padding: 8px; border: 1px solid #ddd; width: 33%;">오후 평균 습도</th>
                <th style="padding: 8px; border: 1px solid #ddd; width: 33%;">전체 평균 습도</th>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">{morning_humidity:.1f}% ({morning_condition} {morning_icon})</td>
                <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">{afternoon_humidity:.1f}% ({afternoon_condition} {afternoon_icon})</td>
                <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">{overall_humidity:.1f}%</td>
            </tr>
        </table>
        
        <div style="background-color: #f9f9f9; padding: 10px; border-left: 4px solid #4a90e2; margin-bottom: 10px;">
            <p><strong>오전 습도 안내:</strong> {morning_msg}</p>
        </div>
        
        <div style="background-color: #f9f9f9; padding: 10px; border-left: 4px solid #4a90e2;">
            <p><strong>오후 습도 안내:</strong> {afternoon_msg}</p>
        </div>
    </div>
    """
    return html


def get_overall_weather(hourly_data: List[Dict[str, Any]]) -> Tuple[str, str]:
    """
    12시간 데이터를 분석하여 종합적인 날씨 상태를 결정합니다.
    
    Args:
        hourly_data (List[Dict[str, Any]]): 시간별 날씨 정보
        
    Returns:
        Tuple[str, str]: (종합 날씨 상태, 날씨 아이콘)
    """
    # 날씨 ID 카운터 초기화
    weather_ids: CounterType[int] = Counter()
    
    # 12시간 동안의 날씨 ID 수집
    for hour in hourly_data:
        weather_id = hour.get("weather", [{}])[0].get("id", 800)
        weather_ids[weather_id] += 1
    
    # 우선순위 그룹 (비, 눈, 뇌우 등의 특별한 날씨 상태는 우선순위가 높음)
    priority_groups = [
        # 뇌우 (200-299)
        [id for id in weather_ids.keys() if 200 <= id <= 299],
        # 비 (300-399, 500-599)
        [id for id in weather_ids.keys() if (300 <= id <= 399) or (500 <= id <= 599)],
        # 눈 (600-699)
        [id for id in weather_ids.keys() if 600 <= id <= 699],
        # 안개 등 (700-799)
        [id for id in weather_ids.keys() if 700 <= id <= 799],
        # 구름/맑음 (800-899)
        [id for id in weather_ids.keys() if 800 <= id <= 899]
    ]
    
    # 우선순위 그룹에서 가장 빈도가 높은 날씨 ID 찾기
    most_significant_id = 800  # 기본값은 맑음
    
    for group in priority_groups:
        if group:
            # 해당 그룹에서 가장 빈도가 높은 날씨 ID 찾기
            group_counts = {id: weather_ids[id] for id in group}
            most_common_id = max(group_counts.items(), key=lambda x: x[1])[0]
            
            # 해당 날씨가 전체 시간의 25% 이상을 차지하면 유의미하다고 판단
            if weather_ids[most_common_id] >= len(hourly_data) / 4:
                most_significant_id = most_common_id
                break
    
    # 날씨 상태와 아이콘 가져오기
    return get_weather_condition(most_significant_id)


def generate_hourly_forecast_html(hourly_data: List[Dict[str, Any]]) -> str:
    """
    12시간 예보 데이터를 HTML 테이블로 생성합니다.
    
    Args:
        hourly_data (List[Dict[str, Any]]): 시간별 날씨 정보
        
    Returns:
        str: HTML 형식의 시간별 예보 테이블
    """
    if not hourly_data:
        return "<p>시간별 예보 정보를 불러올 수 없습니다.</p>"
    
    html = """
    <table style="width:100%; border-collapse: collapse; text-align: center;">
    <tr style="background-color: #f2f2f2;">
        <th style="padding: 8px; border: 1px solid #ddd;">시간</th>
        <th style="padding: 8px; border: 1px solid #ddd;">날씨</th>
        <th style="padding: 8px; border: 1px solid #ddd;">온도</th>
        <th style="padding: 8px; border: 1px solid #ddd;">습도</th>
    </tr>
    """
    
    for hour in hourly_data:
        # 데이터 추출
        dt = hour.get("dt", 0)
        temp = hour.get("temp", 0)
        humidity = hour.get("humidity", 0)
        weather = hour.get("weather", [{}])[0]
        weather_id = weather.get("id", 800)
        
        # Unix 시간을 KST 시:분 형식으로 변환
        time_str = to_kst(dt).strftime("%H:%M")
        
        # 날씨 상태 및 아이콘
        condition, icon = get_weather_condition(weather_id)
        
        # 행 추가
        html += f"""
        <tr>
            <td style="padding: 8px; border: 1px solid #ddd;">{time_str}</td>
            <td style="padding: 8px; border: 1px solid #ddd;">{condition} {icon}</td>
            <td style="padding: 8px; border: 1px solid #ddd;">{temp:.1f}°C</td>
            <td style="padding: 8px; border: 1px solid #ddd;">{humidity}%</td>
        </tr>
        """
    
    html += "</table>"
    return html


def check_precipitation_forecast(hourly_data: List[Dict[str, Any]]) -> Tuple[bool, bool, bool, bool]:
    """
    시간별 날씨 데이터에서 비와 눈 예보를 확인합니다.
    
    Args:
        hourly_data (List[Dict[str, Any]]): 시간별 날씨 정보
        
    Returns:
        Tuple[bool, bool, bool, bool]: (비 예보 여부, 눈 예보 여부, 소나기 여부, 강한 비 여부)
    """
    will_rain = False
    will_snow = False
    will_shower = False
    will_heavy_rain = False
    
    for hour in hourly_data:
        weather_id = hour.get("weather", [{}])[0].get("id", 800)
        
        # 소나기 확인 (500-504, 520-531)
        if (500 <= weather_id <= 504) or (520 <= weather_id <= 531):
            will_rain = True
            will_shower = True
            
        # 일반 비 확인 (511: 보통의 비)
        elif weather_id == 511:
            will_rain = True
            
        # 강한 비 확인 (502-504, 522-531)
        elif (502 <= weather_id <= 504) or (522 <= weather_id <= 531):
            will_rain = True
            will_heavy_rain = True
            
        # 눈 예보 확인 (600-622: 눈)
        elif 600 <= weather_id <= 622:
            will_snow = True
            
        # 모든 상태가 확인되면 루프 종료
        if will_rain and will_snow and will_shower and will_heavy_rain:
            break
            
    return will_rain, will_snow, will_shower, will_heavy_rain


# 이메일 전송 
def send_email(subject: str, body: str) -> bool:
    """
    이메일을 전송하는 함수 입니다. - 일반 SMTP를 사용합니다.
    
    Args:
        subject: 이메일 제목
        body: HTML 형식의 이메일 내용
    
    Returns:
        bool: 이메일 전송 성공 여부
    """
    # 수신자 설정
    to_recipients = [RECIPIENT] if RECIPIENT else []
    bcc_recipients = BCC_RECIPIENTS if BCC_RECIPIENTS else []
    
    # 수신자가 없으면 종료
    if not to_recipients and not bcc_recipients:
        logging.error("수신자가 설정되지 않았습니다.")
        return False
    
    # 모든 수신자 목록 (To + BCC)
    all_recipients = to_recipients.copy()  # 새 리스트 생성
    all_recipients.extend(bcc_recipients)  # 리스트에 리스트 추가
    
    # 메일 생성
    msg = MIMEMultipart('related')
    msg['Subject'] = subject
    msg['From'] = SMTP_FROM
    msg['To'] = ", ".join(to_recipients) if to_recipients else ""  # 표시되는 수신자에는 BCC 제외
    msg.preamble = 'This is a multi-part message in MIME format.'
    
    # 대체 콘텐츠 컨테이너 생성
    msgAlternative = MIMEMultipart('alternative')
    msg.attach(msgAlternative)
    
    # 메일 본문 내용 작성
    msgText = MIMEText(body, 'html', _charset="utf8")
    msgAlternative.attach(msgText)
    
    smtp_port = int(SMTP_PORT) if SMTP_PORT else 587

    for attempt in range(1, 4):
        try:
            logging.info(f"SMTP로 이메일 전송 시도 ({SMTP_HOST}:{smtp_port})... [{attempt}/3]")

            if smtp_port == 465:
                server = smtplib.SMTP_SSL(SMTP_HOST, smtp_port, timeout=30)
            else:
                server = smtplib.SMTP(SMTP_HOST, smtp_port, timeout=30)
                server.ehlo()
                server.starttls()
                server.ehlo()

            try:
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.sendmail(SMTP_FROM, all_recipients, msg.as_string())
            finally:
                server.quit()

            to_log = ", ".join(to_recipients) if to_recipients else "없음"
            bcc_log = ", ".join(bcc_recipients) if bcc_recipients else "없음"

            logging.info(f"이메일 전송 완료: {subject}")
            logging.info(f"수신자(TO): {to_log}")
            logging.info(f"수신자(BCC): {bcc_log}")
            return True

        except Exception as e:
            logging.error(f"이메일 전송 중 오류 발생: {e}")
            if hasattr(e, "smtp_code"):
                logging.error(f"SMTP 코드: {e.smtp_code}")
            if hasattr(e, "smtp_error"):
                logging.error(f"SMTP 오류: {e.smtp_error}")
            if attempt < 3:
                time.sleep(5)

    return False