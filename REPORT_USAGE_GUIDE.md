# 📋 Report 모드 사용 가이드

## 🚀 전체 데이터 처리 방법

### 1. 자동 배치 실행 (권장)
```bash
# 전체 자동 처리 (백그라운드 실행 + 진행 모니터링)
./run_batch_reports.sh
```

### 2. 수동 배치 실행
```bash
# 2-1. 백그라운드에서 실행
nohup python src/main.py > logs/batch_$(date +%Y%m%d_%H%M%S).log 2>&1 &

# 2-2. 진행 상황 확인
tail -f logs/batch_*.log
```

### 3. 포그라운드 실행 (작은 데이터셋)
```bash
# 설정 확인 후 직접 실행
python src/main.py
```

## 📄 PDF 출력 설정

### 방법 1: HTML 변환 (현재 지원)
```bash
# 개별 파일 변환
python src/html_pdf_generator.py --html-only outputs/reports/student/학생_20114.md

# 전체 폴더 변환
python src/html_pdf_generator.py --batch outputs/reports/student/
python src/html_pdf_generator.py --batch outputs/reports/teacher/
```

### 방법 2: Pandoc 변환 (선택사항)
```bash
# Pandoc 설치 (Ubuntu/Debian)
sudo apt-get install pandoc texlive-xetex texlive-fonts-recommended

# 변환 실행
python src/pdf_generator.py --batch outputs/reports/student/
```

## 🎯 모드 전환 방법

### Report 모드 활성화
```bash
# config.yaml 수정
sed -i 's/mode: .*/mode: report/' configs/config.yaml
```

### 다른 모드로 전환
```bash
# Summary 모드
sed -i 's/mode: .*/mode: summary/' configs/config.yaml

# Integration 모드
sed -i 's/mode: .*/mode: integration_v6/' configs/config.yaml
```

## 📊 결과 확인

### 생성된 파일 위치
```bash
# 학생용 리포트
ls -la outputs/reports/student/

# 교사용 리포트
ls -la outputs/reports/teacher/

# HTML 파일 (PDF 변환용)
ls -la outputs/reports/student/*.html
ls -la outputs/reports/teacher/*.html
```

### 처리 통계 확인
```bash
# 처리된 학생 수
ls outputs/reports/student/*.md | wc -l

# 전체 학생 폴더 수
ls -d data/conversation_math/*/ | wc -l
```

## 🔧 고급 설정

### 1. 출력 형식 설정 (configs/mode/report.yaml)
```yaml
output_formats:
  - "md"      # 기본 Markdown
  - "pdf"     # PDF 출력 (pandoc 필요)
  - "html"    # HTML 출력
```

### 2. 처리 대상 설정
```yaml
input_dirs:
  - "/path/to/conversation_data/"
  
file_patterns:
  folder_pattern: "(.+)_([a-f0-9]{8})"  # 폴더명 패턴
  chat_file_pattern: "chats_*.txt"       # 파일명 패턴
```

### 3. 프롬프트 커스터마이징
```bash
# 학생용 프롬프트 수정
nano prompts/report/report_student.txt

# 교사용 프롬프트 수정
nano prompts/report/report_teacher.txt
```

## 🚨 문제 해결

### 1. 처리 중단 시
```bash
# 백그라운드 프로세스 확인
ps aux | grep "python src/main.py"

# 프로세스 종료
kill -9 [PID]
```

### 2. 메모리 부족 시
```bash
# 모니터링
htop

# 처리 대상 분할
# configs/mode/report.yaml에서 input_dirs를 작은 단위로 분할
```

### 3. PDF 생성 문제
```bash
# HTML 대안 사용 (브라우저에서 PDF 저장)
python src/html_pdf_generator.py --html-only [파일명]

# 브라우저에서 HTML 열기 → 인쇄 → PDF로 저장
```

## 📈 성능 최적화

### 1. 병렬 처리
```bash
# 여러 터미널에서 다른 폴더 처리
# Terminal 1: 학생_201XX 처리
# Terminal 2: 학생_204XX 처리
```

### 2. 로그 레벨 조정
```python
# src/main.py의 logging 설정 수정
logging.basicConfig(level=logging.WARNING)  # INFO → WARNING
```

### 3. 모델 최적화
```yaml
# configs/llm/gemini_flash.yaml
max_tokens: 8192      # 토큰 제한 조정
temperature: 0.2      # 일관성 향상
```

## 💡 활용 팁

### 1. 정기적인 배치 실행
```bash
# Cron 설정 예시
# 매일 오전 2시 실행
0 2 * * * cd /path/to/critical_analyzer && ./run_batch_reports.sh
```

### 2. 결과 백업
```bash
# 날짜별 백업
cp -r outputs/reports outputs/reports_backup_$(date +%Y%m%d)
```

### 3. 대용량 데이터 처리
```bash
# 단계별 처리
# 1단계: 일부 데이터로 테스트
# 2단계: 전체 데이터 처리
# 3단계: 결과 검증 및 PDF 변환
```

---

**💡 참고**: 전체 데이터 처리는 시간이 오래 걸릴 수 있습니다. 
백그라운드 실행을 권장하며, 진행 상황을 주기적으로 모니터링하세요.