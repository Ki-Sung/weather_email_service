## 유틸리티 함수 모음
import gc
import os
import logging
import psutil
import time
from datetime import datetime
import datetime as dt
from zoneinfo import ZoneInfo

from config.settings import TIMEZONE, FORECAST_START_HOUR, FORECAST_HOURS

KST = ZoneInfo(TIMEZONE)
from enum import Enum
from typing import Tuple, List, Dict, Any

# 열거형 클래스 정의 - 날씨 상태 코드에 따른 설명
class WeatherCondition(Enum):
    THUNDERSTORM = "천둥번개"
    DRIZZLE = "이슬비"
    LIGHT_RAIN = "가벼운 비"
    MODERATE_RAIN = "비"
    HEAVY_RAIN = "강한 비"
    SHOWER_RAIN = "소나기"
    SNOW = "눈"
    ATMOSPHERE = "안개"
    CLEAR = "맑음"
    PARTLY_CLOUDY = "구름 조금"
    CLOUDS = "구름 많음"

# 열거형 클래스 정의 - 습도 상태에 따른 설명
class HumidityCondition(Enum):
    VERY_DRY = "매우 건조"
    DRY = "건조"
    OPTIMAL = "적정"
    HUMID = "습함"
    VERY_HUMID = "매우 습함"

# 날씨 아이콘 - 날씨 상태별로 사용할 이모지 아이콘 정의 
WEATHER_ICONS = {
    "THUNDERSTORM": "⚡",
    "DRIZZLE": "🌦️",
    "LIGHT_RAIN": "🌦️",
    "MODERATE_RAIN": "☔",
    "HEAVY_RAIN": "🌧️",
    "SHOWER_RAIN": "🌦️",
    "SNOW": "❄️",
    "ATMOSPHERE": "🌫️",
    "CLEAR": "☀️",
    "PARTLY_CLOUDY": "⛅",
    "CLOUDS": "☁️"
}

# 습도 아이콘 - 습도 상태별로 사용할 이모지 아이콘 정의
HUMIDITY_ICONS = {
    "VERY_DRY": "🏜️",
    "DRY": "📉",
    "OPTIMAL": "👍",
    "HUMID": "💧",
    "VERY_HUMID": "💦"
}

# 열거형 클레스 정의 - 미세먼지 단계
class AirQualityLevel(Enum):
    GOOD = "좋음"
    FAIR = "보통"
    MODERATE = "약간 나쁨"
    POOR = "나쁨" 
    VERY_POOR = "매우 나쁨"


# 날씨 코드에 따른 상태와 아이콘을 반환하는 함수
def get_weather_condition(code: int) -> Tuple[str, str]:
    """ 
    OpenWeatherMap에서 제공하는 날씨 코드(code)를 기반으로
    날씨 상태(예: 맑음, 비)와 해당 아이콘을 반환하는 함수입니다.
    
    Args:
        code: 날씨 코드
            200-299: 천둥번개
            300-399: 이슬비
            500-504: 가벼운 소나기
            511: 보통의 비
            520-531: 소나기
            600-699: 눈
            700-799: 안개
            800: 맑음
            801: 구름 조금
            802-899: 구름 많음
        
    Returns:
        Tuple[str, str]: 날씨 상태와 아이콘
    """
    if 200 <= code < 300:
        return WeatherCondition.THUNDERSTORM.value, WEATHER_ICONS["THUNDERSTORM"]
    elif 300 <= code < 400:
        return WeatherCondition.DRIZZLE.value, WEATHER_ICONS["DRIZZLE"]
    elif 500 <= code <= 504:  # 가벼운 소나기
        return WeatherCondition.SHOWER_RAIN.value, WEATHER_ICONS["SHOWER_RAIN"]
    elif code == 511:  # 보통의 비
        return WeatherCondition.MODERATE_RAIN.value, WEATHER_ICONS["MODERATE_RAIN"]
    elif 520 <= code <= 531:  # 소나기
        return WeatherCondition.SHOWER_RAIN.value, WEATHER_ICONS["SHOWER_RAIN"]
    elif 600 <= code < 700:
        return WeatherCondition.SNOW.value, WEATHER_ICONS["SNOW"]
    elif 700 <= code < 800:
        return WeatherCondition.ATMOSPHERE.value, WEATHER_ICONS["ATMOSPHERE"]
    elif code == 800:
        return WeatherCondition.CLEAR.value, WEATHER_ICONS["CLEAR"]
    elif code == 801:
        return WeatherCondition.PARTLY_CLOUDY.value, WEATHER_ICONS["PARTLY_CLOUDY"]
    else:  # 802-899
        return WeatherCondition.CLOUDS.value, WEATHER_ICONS["CLOUDS"]


# 대기 질 인덱스에 따른 상태를 반환하는 함수
def get_air_quality_level(aqi: int) -> Tuple[str, str]:
    """
    대기 질 인덱스(AQI: Air Quality Index) 값에 따라
    미세먼지 상태(예: 좋음, 나쁨)와 그에 따른 간단한 조언 메시지를 반환하는 함수입니다.
    
    Args:
        aqi: 대기 질 인덱스 값
            1: 좋음
            2: 보통
            3: 약간 나쁨
            4: 나쁨
            5: 매우 나쁨
    Returns:
        Tuple[str, str]: 미세먼지 상태와 조언 메시지
    """
    if aqi == 1:
        return AirQualityLevel.GOOD.value, "미세먼지가 거의 없으니 마음껏 활동하세요!"
    elif aqi == 2:
        return AirQualityLevel.FAIR.value, "미세먼지가 보통이에요."
    elif aqi == 3:
        return AirQualityLevel.MODERATE.value, "민감하신 분들은 마스크 착용을 권장합니다."
    elif aqi == 4:
        return AirQualityLevel.POOR.value, "미세먼지가 나쁘니 마스크를 착용하세요."
    else:
        return AirQualityLevel.VERY_POOR.value, "미세먼지가 매우 나쁘니 외출을 자제하고 마스크를 꼭 착용하세요!"


# 계절별 온도에 따른 조언을 반환하는 함수
def get_season_advice(temp_max: float, temp_min: float) -> str:
    """
    현재 온도에 따른 조언을 반환합니다.
    
    Args:
        temp_max: 오늘의 최고 온도
        temp_min: 오늘의 최저 온도
    Returns:
        str: 계절별 조언 메시지
    """
    
    # 현재 월 추출
    current_month = dt.datetime.now().month
    
    # 조언 메시지 초기화
    advice = ""
    
    # 여름철 (6-8월) -> 폭염 조언 추가 (기준 33도 이상)
    if 6 <= current_month <= 8:
        if temp_max >= 33:
            advice = "폭염이 예상되니 충분한 수분 섭취와 건강관리에 유의하세요. 🔥"
    
    # 겨울철 (12-2월) -> 한파 조언 추가 (기준 -12도 이하)
    elif current_month == 12 or 1 <= current_month <= 2:
        if temp_min <= -12:
            advice = "한파 주의보가 발령되었습니다. 옷을 따뜻하게 입고 외출시 체온 관리에 유의하세요. ❄️"
    
    return advice


# 날씨 상태에 따른 메시지를 반환하는 함수
def get_weather_message(condition: str) -> str:
    """
    날씨 상태에 따른 메시지를 반환합니다.
    
    Args:
        condition: 날씨 상태 (예: 맑음, 비 등)
    Returns:
        str: 날씨 상태에 따른 메시지
    """
    # 날씨 상태에 따른 메시지 설정
    if condition == WeatherCondition.CLEAR.value:
        return "오늘은 맑은 날씨입니다. 야외 활동하기 좋은 날이에요! 🌞"
    elif condition == WeatherCondition.PARTLY_CLOUDY.value:
        return "구름이 조금 있지만 대체로 맑은 날씨입니다. 🌤️"
    elif condition == WeatherCondition.CLOUDS.value:
        return "오늘은 구름이 많아요. 햇빛이 약할 수 있어요. ☁️"
    elif condition == WeatherCondition.LIGHT_RAIN.value:
        return "가벼운 비가 내릴 수 있어요. 우산을 챙기세요. 🌦️"
    elif condition == WeatherCondition.MODERATE_RAIN.value:
        return "오늘은 비가 예상되니 우산을 꼭 챙기세요! ☔"
    elif condition == WeatherCondition.HEAVY_RAIN.value:
        return "강한 비가 예상됩니다. 외출을 자제하고 우산을 꼭 챙기세요! 🌧️"
    elif condition == WeatherCondition.SHOWER_RAIN.value:
        return "소나기가 내릴 수 있어요. 갑작스러운 날씨 변화에 대비하세요! 🌦️"
    elif condition == WeatherCondition.SNOW.value:
        return "눈이 내릴 예정이에요. 미끄러지지 않게 조심하세요! ❄️"
    elif condition == WeatherCondition.THUNDERSTORM.value:
        return "천둥번개가 칠 수 있으니 야외 활동을 자제하세요. ⚡"
    elif condition == WeatherCondition.DRIZZLE.value:
        return "이슬비가 내릴 수 있어요. 우산을 챙기세요. 🌦️"
    elif condition == WeatherCondition.ATMOSPHERE.value:
        return "안개가 끼었습니다. 운전 시 주의하세요. 🌫️"
    else:
        return "오늘도 좋은 하루 되세요!"
    

# 온도와 계절에 따른 적정 습도 범위를 반환하는 함수
def get_optimal_humidity_range(temp: float, month: int) -> Tuple[int, int]:
    """
    현재 온도와 계절(월)에 따른 적정 습도 범위를 반환합니다.
    
    Args:
        temp: 현재 온도 (°C)
        month: 현재 월 (1-12)
    
    Returns:
        Tuple[int, int]: (최소 적정 습도, 최대 적정 습도)
    """
    # 온도에 따른 적정 습도 범위
    if temp < 15:
        min_optimal, max_optimal = 60, 70
    elif 15 <= temp < 18:
        min_optimal, max_optimal = 60, 70
    elif 18 <= temp < 21:
        min_optimal, max_optimal = 50, 60
    elif 21 <= temp < 24:
        min_optimal, max_optimal = 45, 55
    else:  # 24도 이상
        min_optimal, max_optimal = 40, 50
    
    # 계절에 따른 적정 습도 보정
    # 봄/가을 (3-5월, 9-11월)
    if 3 <= month <= 5 or 9 <= month <= 11:
        season_min, season_max = 45, 55
    # 여름 (6-8월)
    elif 6 <= month <= 8:
        season_min, season_max = 50, 60
    # 겨울 (12, 1-2월)
    else:
        season_min, season_max = 35, 45
    
    # 온도와 계절 기준의 적정 습도 범위 중 넓은 범위 선택
    min_humidity = min(min_optimal, season_min)
    max_humidity = max(max_optimal, season_max)
    
    return min_humidity, max_humidity


# 습도 상태와 메시지를 반환하는 함수
def get_humidity_condition(current_humidity: float, min_optimal: int, max_optimal: int) -> Tuple[str, str, str]:
    """
    현재 습도와 적정 습도 범위를 비교하여 습도 상태와 메시지를 반환합니다.
    
    Args:
        current_humidity: 현재 습도 (%)
        min_optimal: 최소 적정 습도 (%)
        max_optimal: 최대 적정 습도 (%)
    
    Returns:
        Tuple[str, str, str]: (습도 상태, 아이콘, 메시지)
    """
    if current_humidity < min_optimal - 20:
        condition = HumidityCondition.VERY_DRY.value
        icon = HUMIDITY_ICONS["VERY_DRY"]
        message = (
            "습도가 매우 낮습니다. 기관지와 피부가 건조해질 수 있으니 가습기 사용을 권장하며, "
            "충분한 수분 섭취와 보습에 신경 써주세요."
        )
    elif current_humidity < min_optimal:
        condition = HumidityCondition.DRY.value
        icon = HUMIDITY_ICONS["DRY"]
        message = (
            "습도가 다소 낮습니다. 기관지 건강을 위해 적절한 실내 습도 유지가 필요합니다. "
            "가습기 사용이나 물을 자주 마시는 것이 도움이 됩니다."
        )
    elif min_optimal <= current_humidity <= max_optimal:
        condition = HumidityCondition.OPTIMAL.value
        icon = HUMIDITY_ICONS["OPTIMAL"]
        message = "현재 습도는 적정 수준입니다. 쾌적한 환경이 유지되고 있어요."
    elif current_humidity <= max_optimal + 20:
        condition = HumidityCondition.HUMID.value
        icon = HUMIDITY_ICONS["HUMID"]
        message = (
            "습도가 다소 높습니다. 실내 환기를 자주 하고, 제습기 사용을 고려해보세요. "
            "곰팡이가 생기기 쉬운 환경이므로 주의가 필요합니다."
        )
    else:
        condition = HumidityCondition.VERY_HUMID.value
        icon = HUMIDITY_ICONS["VERY_HUMID"]
        message = (
            "습도가 매우 높습니다. 불쾌지수가 높을 수 있으니 제습기 사용과 충분한 환기가 필요합니다. "
            "실내 곰팡이 번식에 주의하고, 음식물은 빨리 상할 수 있으니 관리에 신경 써주세요."
        )
    
    return condition, icon, message


def to_kst(unix_ts: int) -> datetime:
    """Unix 타임스탬프를 KST datetime으로 변환합니다."""
    return datetime.fromtimestamp(unix_ts, tz=KST)


def get_hourly_forecast_from_kst(
    hourly_data: List[Dict[str, Any]],
    start_hour: int = FORECAST_START_HOUR,
    count: int = FORECAST_HOURS,
) -> List[Dict[str, Any]]:
    """오늘 KST start_hour부터 count개의 시간별 예보를 반환합니다."""
    if not hourly_data:
        return []

    today = datetime.now(KST).date()
    start_ts = datetime(
        today.year, today.month, today.day, start_hour, 0, 0, tzinfo=KST
    ).timestamp()

    filtered = [hour for hour in hourly_data if hour.get("dt", 0) >= start_ts]
    return filtered[:count] if filtered else hourly_data[:count]


# 시간대별 습도를 분석하여 오전/오후 평균 습도 계산
def analyze_humidity(hourly_data: List[Dict[str, Any]]) -> Dict[str, float]:
    """
    시간대별 습도 데이터를 분석하여 오전과 오후의 평균 습도를 계산합니다.
    
    Args:
        hourly_data (List[Dict[str, Any]]): 시간별 날씨 정보
    
    Returns:
        Dict[str, float]: 오전/오후/전체 평균 습도 정보
    """
    if not hourly_data:
        return {"morning_avg": 0, "afternoon_avg": 0, "overall_avg": 0}
    
    morning_humidity = []
    afternoon_humidity = []
    
    for hour in hourly_data:
        dt_value = hour.get("dt", 0)
        humidity = hour.get("humidity", 0)
        
        # Unix 시간을 KST 기준 시간으로 변환
        hour_of_day = to_kst(dt_value).hour
        
        # 오전(0-11시)과 오후(12-23시)로 구분
        if 0 <= hour_of_day < 12:
            morning_humidity.append(humidity)
        else:
            afternoon_humidity.append(humidity)
    
    # 평균 계산 (데이터가 없는 경우 0으로 처리)
    morning_avg = sum(morning_humidity) / len(morning_humidity) if morning_humidity else 0
    afternoon_avg = sum(afternoon_humidity) / len(afternoon_humidity) if afternoon_humidity else 0
    overall_avg = sum([h.get("humidity", 0) for h in hourly_data]) / len(hourly_data) if hourly_data else 0
    
    return {
        "morning_avg": morning_avg,
        "afternoon_avg": afternoon_avg,
        "overall_avg": overall_avg
    }

# 메모리 정리 및 로그 기록 함수
def memory_cleanup():
    """
    가비지 컬렉션을 강제 실행하고 메모리 사용량을 기록합니다.
    
    Returns:
        int: 수집된 객체 수
    """
    # 시작 메모리 사용량 기록
    # 현재 프로세스 정보 가져오기 
    process = psutil.Process(os.getpid())
    
    # 시작 메모리 사용량 기록 (RSS: Resident Set Size)
    start_memory = process.memory_info().rss / 1024 / 1024  # MB 단위로 변환
    
    # 가비지 컬렉션 강제 실행
    collected = gc.collect(2)  # 모든 세대의 객체 수집 (2: 모든 세대)
    
    # 종료 메모리 사용량 기록
    end_memory = process.memory_info().rss / 1024 / 1024  # MB 단위로 변환
    
    # 로그 기록: 회수된 객체 수와 메모리 사용량 차이 기록
    logging.info(f"메모리 정리 수행: {collected}개 객체 회수")
    logging.info(f"메모리 사용량: {start_memory:.2f}MB -> {end_memory:.2f}MB (차이: {start_memory - end_memory:.2f}MB)")
    
    return collected


# 로그 파일 회전 함수
def log_rotation(log_file, max_size_mb=10, backup_count=5):
    """
    로그 파일이 특정 크기를 초과하면 로테이션합니다.
    
    Args:
        log_file: 로그 파일 경로
        max_size_mb: 최대 로그 파일 크기 (MB)
        backup_count: 보관할 백업 파일 수
    """
    # 로그 파일이 존재하지 않으면 종료
    if not os.path.exists(log_file):
        return
        
    # 현재 로그 파일 크기 확인 (MB 단위로 변환)
    file_size_mb = os.path.getsize(log_file) / (1024 * 1024)
    
    # 로그 파일 크기가 최대 크기를 초과하는 경우 
    if file_size_mb >= max_size_mb:
        # 기존 백업 파일 처리
        for i in range(backup_count - 1, 0, -1):
            old_backup = f"{log_file}.{i}"                  # 기존 백업 파일 이름 
            new_backup = f"{log_file}.{i+1}"                # 새로운 백업 파일 이름      
            
            # 기존 백업 파일이 존재할 경우 
            if os.path.exists(old_backup):
                # 새로운 백업 파일이 존재할 경우 삭제
                if os.path.exists(new_backup):
                    os.remove(new_backup)
                    
                # 기존 백업 파일을 새로운 백업 파일로 이름 변경
                os.rename(old_backup, new_backup)
                
        # 현재 로그 파일을 첫 번째 백업으로 이동
        backup_1 = f"{log_file}.1"
        
        # 첫 번째 백업 파일이 존재할 경우 삭제
        if os.path.exists(backup_1):
            os.remove(backup_1)
        
        # 현재 로그 파일을 첫 번째 백업 파일로 이름 변경
        os.rename(log_file, backup_1)
        
        # 새 로그 파일 생성 메시지
        with open(log_file, 'w') as f:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            f.write(f"===== 새 로그 파일 생성: {timestamp} =====\n")
        
        # 로그 기록: 로그 파일 로테이션 수행 메시지
        logging.info(f"로그 파일 로테이션 수행: {file_size_mb:.2f}MB -> 0MB")