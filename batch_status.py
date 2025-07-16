#!/usr/bin/env python3
"""
배치 처리 상태 모니터링 도구
"""

import os
import time
from pathlib import Path
from datetime import datetime
import subprocess

def get_batch_status():
    """배치 처리 상태 확인"""
    print("📊 배치 처리 상태 모니터링")
    print("=" * 60)
    
    # 1. 프로세스 상태 확인
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        main_processes = [line for line in result.stdout.split('\n') if 'python src/main.py' in line]
        
        if main_processes:
            print("✅ 배치 프로세스 실행 중:")
            for proc in main_processes:
                parts = proc.split()
                pid = parts[1]
                cpu = parts[2]
                mem = parts[3]
                runtime = parts[9]
                print(f"   PID: {pid}, CPU: {cpu}%, MEM: {mem}%, Runtime: {runtime}")
        else:
            print("❌ 배치 프로세스가 실행되지 않음")
    except Exception as e:
        print(f"❌ 프로세스 상태 확인 실패: {e}")
    
    print()
    
    # 2. 파일 생성 현황
    total_data_files = len(list(Path("data/conversation_math").glob("*/chats_*.txt")))
    
    md_files = len(list(Path("outputs/reports").glob("**/*.md")))
    html_files = len(list(Path("outputs/reports").glob("**/*.html")))
    pdf_files = len(list(Path("outputs/reports").glob("**/*.pdf")))
    
    student_md = len(list(Path("outputs/reports/student").glob("*.md")))
    teacher_md = len(list(Path("outputs/reports/teacher").glob("*.md")))
    
    print("📁 파일 생성 현황:")
    print(f"   전체 대상 파일: {total_data_files}개")
    print(f"   마크다운 파일: {md_files}개 (학생: {student_md}, 교사: {teacher_md})")
    print(f"   HTML 파일: {html_files}개")
    print(f"   PDF 파일: {pdf_files}개")
    
    progress = (md_files // 2) / total_data_files * 100 if total_data_files > 0 else 0
    print(f"   진행률: {progress:.1f}% ({md_files//2}/{total_data_files})")
    
    print()
    
    # 3. 로그 파일 확인
    log_files = list(Path("logs").glob("*.log"))
    if log_files:
        latest_log = max(log_files, key=os.path.getmtime)
        print(f"📋 최신 로그 파일: {latest_log}")
        
        # 로그 파일 크기
        log_size = os.path.getsize(latest_log)
        print(f"   로그 크기: {log_size:,} bytes")
        
        # 최근 업데이트 시간
        mod_time = os.path.getmtime(latest_log)
        last_update = datetime.fromtimestamp(mod_time).strftime("%Y-%m-%d %H:%M:%S")
        print(f"   마지막 업데이트: {last_update}")
        
        # 최근 로그 내용 (마지막 5줄)
        print("   최근 로그 내용:")
        try:
            with open(latest_log, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                for line in lines[-5:]:
                    print(f"     {line.strip()}")
        except Exception as e:
            print(f"     로그 읽기 실패: {e}")
    else:
        print("📋 로그 파일이 없습니다.")
    
    print()
    
    # 4. 예상 완료 시간 계산
    if md_files > 0:
        # 평균 처리 시간 추정 (약 1.5분/파일)
        avg_time_per_file = 1.5  # 분
        remaining_files = total_data_files - (md_files // 2)
        estimated_time = remaining_files * avg_time_per_file
        
        print(f"⏱️  예상 완료 시간: {estimated_time:.1f}분 후")
        
        if estimated_time > 0:
            completion_time = datetime.now().timestamp() + (estimated_time * 60)
            completion_str = datetime.fromtimestamp(completion_time).strftime("%Y-%m-%d %H:%M:%S")
            print(f"   완료 예상 시각: {completion_str}")
    
    print("=" * 60)

def monitor_continuous():
    """연속 모니터링 모드"""
    print("🔄 연속 모니터링 모드 시작 (Ctrl+C로 종료)")
    print()
    
    try:
        while True:
            os.system('clear')  # 화면 지우기
            get_batch_status()
            print("(10초마다 자동 업데이트)")
            time.sleep(10)
    except KeyboardInterrupt:
        print("\n👋 모니터링 종료")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--monitor":
        monitor_continuous()
    else:
        get_batch_status()