#!/bin/bash
# 전체 데이터 배치 리포트 생성 스크립트

echo "🚀 전체 데이터 배치 리포트 생성 시작..."

# 로그 디렉토리 생성
mkdir -p logs

# 현재 시간 기록
TIMESTAMP=$(date "+%Y%m%d_%H%M%S")
LOG_FILE="logs/batch_report_${TIMESTAMP}.log"

echo "📝 로그 파일: $LOG_FILE"

# 백그라운드에서 실행
nohup python src/main.py > "$LOG_FILE" 2>&1 &
PID=$!

echo "🔄 프로세스 ID: $PID"
echo "📊 실행 상태를 확인하려면: tail -f $LOG_FILE"

# 진행 상황 모니터링
echo "📈 진행 상황 모니터링 (Ctrl+C로 종료)"
echo "=================================="

while kill -0 $PID 2>/dev/null; do
    # 완료된 학생 수 계산
    COMPLETED=$(grep -c "Completed processing:" "$LOG_FILE" 2>/dev/null || echo "0")
    TOTAL=$(ls -d data/conversation_math/*/ 2>/dev/null | wc -l)
    
    # 진행률 계산
    if [ "$TOTAL" -gt 0 ]; then
        PROGRESS=$((COMPLETED * 100 / TOTAL))
        echo "📊 진행률: $COMPLETED/$TOTAL ($PROGRESS%)"
    fi
    
    sleep 10
done

echo "✅ 배치 처리 완료!"
echo "📁 결과 위치:"
echo "  - 학생용: outputs/reports/student/"
echo "  - 교사용: outputs/reports/teacher/"

# 결과 요약
STUDENT_COUNT=$(ls outputs/reports/student/*.md 2>/dev/null | wc -l)
TEACHER_COUNT=$(ls outputs/reports/teacher/*.md 2>/dev/null | wc -l)

echo "📊 생성된 리포트:"
echo "  - 학생용: ${STUDENT_COUNT}개"
echo "  - 교사용: ${TEACHER_COUNT}개"

# PDF 변환 실행 (pandoc 설치된 경우)
if command -v pandoc &> /dev/null; then
    echo "📄 PDF 변환 시작..."
    python src/pdf_generator.py --batch outputs/reports/student/
    python src/pdf_generator.py --batch outputs/reports/teacher/
    echo "✅ PDF 변환 완료"
else
    echo "⚠️ pandoc이 설치되지 않아 PDF 변환을 건너뜁니다."
    echo "설치 방법: sudo apt-get install pandoc texlive-xetex texlive-fonts-recommended"
fi

echo "🎉 모든 작업 완료!"