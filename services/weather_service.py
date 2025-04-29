## 날씨 데이터 서비스
import requests
from typing import Dict, Any, Optional

from config.settings import OWM_API_KEY, OWM_ENDPOINT, AIR_POLLUTION_ENDPOINT, SEOUL_LAT, SEOUL_LON

# 날씨 데이터 가져오기 
async def get_weather_data() -> Dict[str, Any]:
    """
    OpenWeatherMap API를 사용하여 서울의 날씨 데이터를 가져옵니다.
    
    Returns:
        Dict[str, Any]: 날씨 데이터 (JSON 형식)
            - 성공 시: 날씨 정보가 포함된 JSON 객체
            - 실패 시: 빈 딕셔너리 반환
    """
    # 날씨 요청 파라미터 설정 
    weather_params = {
        "lat": SEOUL_LAT,                       # 서울 위도 
        "lon": SEOUL_LON,                       # 서울 경도 
        "appid": OWM_API_KEY,                   # OpenWeatherMap API 키 
        "exclude": "minutely",                  # 분 단위 데이터 제외 
        "units": "metric"                       # 섭씨 온도로 변환
    }
    
    try:
        # 날씨 데이터 요청 
        response = requests.get(OWM_ENDPOINT, params=weather_params)
        response.raise_for_status()             # 요청 실패 시 예외 발생 
        return response.json()                  # JSON 형식으로 반환 
    
    except requests.RequestException as e:
        print(f"날씨 데이터 가져오기 실패: {e}")      # 오류 메시지 출력 
        return {}                               # 빈 딕셔너리 반환 
    

# 대기 질 데이터 가져오기 
async def get_air_quality() -> Optional[Dict[str, Any]]:
    """
    OpenWeatherMap API를 사용하여 서울의 대기 질 데이터를 가져옵니다.
    
    Returns:
        Optional[Dict[str, Any]]: 대기 질 데이터 (JSON 형식)
            - 성공 시: 대기 질 정보가 포함된 JSON 객체
            - 실패 시: None 반환
    """
    # 대기 질 요청 파라미터 설정 
    air_params = {
        "lat": SEOUL_LAT,                           # 서울 위도 
        "lon": SEOUL_LON,                           # 서울 경도 
        "appid": OWM_API_KEY                        # OpenWeatherMap API 키 
    }
    
    try:
        # 대기 질 데이터 요청
        response = requests.get(AIR_POLLUTION_ENDPOINT, params=air_params)
        if response.status_code != 200:
            return None                             # 응답 코드가 200이 아닐 경우 None 반환 
        return response.json()                      # JSON 형식으로 반환 
    
    except requests.RequestException as e:
        print(f"대기질 데이터 가져오기 실패: {e}")         # 오류 메시지 출력 
        return None                                 # None 반환 