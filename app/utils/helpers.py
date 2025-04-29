## 유틸리티 함수 모음
import gc
import os
import logging
import psutil
from datetime import datetime
import datetime as dt
from enum import Enum
from typing import Tuple

# 열거형 클래스 정의 - 날씨 상태 코드에 따른 설명
class WeatherCondition(Enum):
    THUNDERSTORM = "천둥번개"
    DRIZZLE = "이슬비"
    RAIN = "비"
    SNOW = "눈"
    ATMOSPHERE = "안개"
    CLEAR = "맑음"
    CLOUDS = "구름"

# 날씨 아이콘 - 날씨 상태별로 사용할 이모지 아이콘 정의 
WEATHER_ICONS = {
    "THUNDERSTORM": "⚡",
    "DRIZZLE": "🌦️",
    "RAIN": "☔",
    "SNOW": "❄️",
    "ATMOSPHERE": "🌫️",
    "CLEAR": "☀️",
    "CLOUDS": "☁️"
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
            300 미만: 천동번개 
            300이상 400미만: 이슬비
            400이상 600미만: 비
            600이상 700미만: 눈
            700이상 800미만: 안개
            800: 맑음
            800 초과: 구름
        
    Returns:
        Tuple[str, str]: 날씨 상태와 아이콘
    """
    if code < 300:
        return WeatherCondition.THUNDERSTORM.value, WEATHER_ICONS["THUNDERSTORM"]
    elif code < 400:
        return WeatherCondition.DRIZZLE.value, WEATHER_ICONS["DRIZZLE"]
    elif code < 600:
        return WeatherCondition.RAIN.value, WEATHER_ICONS["RAIN"]
    elif code < 700:
        return WeatherCondition.SNOW.value, WEATHER_ICONS["SNOW"]
    elif code < 800:
        return WeatherCondition.ATMOSPHERE.value, WEATHER_ICONS["ATMOSPHERE"]
    elif code == 800:
        return WeatherCondition.CLEAR.value, WEATHER_ICONS["CLEAR"]
    else:
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
    # 날씨 상테에 따른 메시지 설정
    if condition == WeatherCondition.CLEAR.value:
        return "오늘은 맑은 날씨입니다. 야외 활동하기 좋은 날이에요! 🌞"
    elif condition == WeatherCondition.RAIN.value:
        return "오늘은 비가 예상되니 우산을 꼭 챙기세요! ☔"
    elif condition == WeatherCondition.SNOW.value:
        return "눈이 내릴 예정이에요. 미끄러지지 않게 조심하세요! ❄️"
    elif condition == WeatherCondition.THUNDERSTORM.value:
        return "천둥번개가 칠 수 있으니 야외 활동을 자제하세요. ⚡"
    elif condition == WeatherCondition.DRIZZLE.value:
        return "이슬비가 내릴 수 있어요. 우산을 챙기세요. 🌦️"
    elif condition == WeatherCondition.CLOUDS.value:
        return "오늘은 구름이 많아요. 햇빛이 약할 수 있어요. ☁️"
    elif condition == WeatherCondition.ATMOSPHERE.value:
        return "안개가 끼었습니다. 운전 시 주의하세요. 🌫️"
    else:
        return "오늘도 좋은 하루 되세요!"
    

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