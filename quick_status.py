#!/usr/bin/env python3
"""
빠른 상태 확인 도구
"""

import subprocess
from pathlib import Path

def quick_status():
    # 파일 개수 확인
    md_files = len(list(Path("outputs/reports").glob("**/*.md")))
    total_files = 41
    completed = md_files // 2
    progress = (completed / total_files) * 100
    
    # 로그에서 현재 처리 중인 학생 찾기
    try:
        with open("logs/batch_report_20250716_214813.log", "r", encoding="utf-8") as f:
            lines = f.readlines()
            for line in reversed(lines):
                if "Processing:" in line:
                    current_student = line.split("Processing: ")[1].split(" (ID:")[0]
                    break
            else:
                current_student = "알 수 없음"
    except:
        current_student = "알 수 없음"
    
    print(f"📊 빠른 상태 확인")
    print(f"진행률: {progress:.1f}% ({completed}/{total_files})")
    print(f"현재 처리 중: {current_student}")
    print(f"남은 학생 수: {total_files - completed}명")
    
    # 예상 완료 시간
    remaining = total_files - completed
    est_minutes = remaining * 1.5
    print(f"예상 완료: {est_minutes:.0f}분 후")

if __name__ == "__main__":
    quick_status()