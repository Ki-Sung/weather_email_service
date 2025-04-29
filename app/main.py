# 날씨 메일 서비스 메인 모듈
import sys
import asyncio
import schedule
import time
import logging
import os
import gc
from datetime import datetime, timedelta

from config.settings import SCHEDULE_TIME
from services.weather_service import get_weather_data, get_air_quality
from services.email_service import create_email_content, send_email
from utils.helpers import memory_cleanup, log_rotation

# 상수 설정
LOG_FILE = "weather_mail.log"                   # 로그 파일 이름 
MEMORY_CLEANUP_INTERVAL = 12                    # 메모리 정리 간격 (시간 단위)
MEMORY_LAST_CLEANUP = datetime.now()            # 마지막 메모리 정리 시간 기록

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),                  # 로그 파일 핸들러 
        logging.StreamHandler()                         # 콘솔 핸들러 
    ]
)
logger = logging.getLogger(__name__)                # 로거 인스턴스 생성 

# 메모리 최적화 설정
gc.enable()                         # 가비지 컬렉션 활성화
gc.set_threshold(700, 10, 5)        # GC 임계값 조정 (기본값보다 약간 공격적)


# 날씨 이메일 전송 함수 
async def send_weather_email():
    """
    날씨 정보를 이메일로 전송합니다.
    """
    # 전역 함수 사용 
    global MEMORY_LAST_CLEANUP
    
    # 로그 기록 
    logger.info(f"날씨 이메일 전송 시작: {datetime.now()}")
    
    try:
        # 로그 파일 확인 및 로테이션
        log_rotation(LOG_FILE)
        
        # 날씨 데이터 가져오기
        weather_data = await get_weather_data()
        air_quality_data = await get_air_quality()
        
        # 이메일 내용 생성
        email_content = create_email_content(weather_data, air_quality_data)
        
        # 이메일 전송
        result = send_email(email_content["subject"], email_content["body"])
        
        # 이메일 전송 결과 로그 기록 
        if result:
            logger.info("날씨 이메일 전송 성공")
        else:
            logger.error("날씨 이메일 전송 실패")
    
    except Exception as e:
        # 오류 로그 기록 
        logger.error(f"날씨 이메일 전송 중 오류 발생: {e}")
    
    finally:
        # 주기적인 메모리 정리 (설정된 간격마다)
        now = datetime.now()
        
        # 메모리 정리 간격 체크 
        if now - MEMORY_LAST_CLEANUP > timedelta(hours=MEMORY_CLEANUP_INTERVAL):
            logger.info("정기 메모리 정리 수행 중...")
            memory_cleanup()
            MEMORY_LAST_CLEANUP = now


# 스케줄러에서 실행할 작업 
def job():
    """
    스케줄러에서 실행할 작업
    """
    # 이벤트 루프 생성 및 설정 
    loop = asyncio.new_event_loop()                     # 새로운 이벤트 루프 생성 
    asyncio.set_event_loop(loop)                        # 생성된 루프 설정 
    
    try:
        loop.run_until_complete(send_weather_email())    # 이메일 전송 작업 실행 
    finally:
        # 작업 완료 후 메모리 정리
        loop.close()                                    # 루프 닫기 
        gc.collect()                                    # 명시적 가비지 컬렉션 


# 스캐줄러 실행 함수 
def run_scheduler():
    """
    스케줄러 실행
    """
    # 로그 기록 
    logger.info(f"날씨 메일 서비스 스케줄러 시작 - 매일 {SCHEDULE_TIME}에 실행")
    logger.info(f"메모리 정리 간격: {MEMORY_CLEANUP_INTERVAL}시간")
    
    # 시작 시 메모리 상태 기록
    memory_cleanup()
    
    # 매일 지정된 시간에 실행
    schedule.every().day.at(SCHEDULE_TIME).do(job)
    
    # 매일 자정에 메모리 정리 작업 추가
    schedule.every().day.at("00:00").do(memory_cleanup)
    
    # 스케줄러 실행
    try:
        while True:
            schedule.run_pending()                          # 스케줄러 실행 
            time.sleep(1)                                   # 1초 대기 
    
    except KeyboardInterrupt:
        logger.info("사용자에 의해 서비스가 중지되었습니다.")        # 예외 처리 
    
    except Exception as e:
        logger.error(f"스케줄러 실행 중 오류 발생: {e}")          # 예외 처리 
    
    finally:
        # 종료 시 메모리 정리
        logger.info("서비스 종료 중... 메모리 정리 수행")
        # 메모리 정리 
        memory_cleanup()

# 즉시 날씨 이메일 전송 함수 
def run_now():
    """즉시 날씨 이메일 전송 (테스트용)"""
    logger.info("날씨 이메일 즉시 전송 테스트")
    
    # 작업 실행 
    job()
    
    # 테스트 후 메모리 정리
    memory_cleanup()

# 메인 실행 함수 
if __name__ == "__main__":
    # 명령행 인수 처리
    if len(sys.argv) > 1 and sys.argv[1] == "--now":
        # 즉시 날씨 이메일 전송 
        run_now()
    else:
        # 스케줄러 실행 
        run_scheduler()