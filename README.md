# Critical Analyzer

## 1. 프로젝트 개요

**Critical Analyzer**는 지정된 폴더 내의 마크다운 문서들을 LLM을 활용하여 심층 분석하고, 세계 최고 수준의 학술지 기준에 입각한 비판적 평가 보고서를 생성하는 파이썬 애플리케이션입니다.

단순 요약을 넘어, 다수의 전문가 페르소나(LLM as a Judge)를 통해 각 문서를 개별적으로 평가하고, 이를 종합하여 전체적인 맥락(Big Picture)을 분석합니다.

## 2. 주요 특징

- **전문가 수준의 비판적 분석**: 탑티어 학술지 편집위원회의 엄격한 기준을 모방한 프롬프트를 통해 연구의 방법론, 이론적 기여도, 실용성을 심층적으로 평가합니다.
- **다중 분석 모드**: 두 가지 핵심 분석 모드를 제공하여 다양한 요구사항에 대응합니다.
    1.  **요약 분석 (Summary Mode)**: 각 문서를 독립적으로 분석하여 상세한 평가 보고서를 개별 파일로 저장하고, 이를 종합하여 전체 컬렉션에 대한 '빅 픽처'와 핵심 테마를 도출합니다.
    2.  **문서 통합 (Integration Mode)**: 하나의 연구 계획 또는 발표를 위한 여러 버전의 초안 문서들을 통합하여, 각 버전의 강점을 취합하고 최적화하여 하나의 완성된 단일 문서를 생성합니다.
- **자동 피드백 생성**: 분석 완료 후, 설정에 따라 PI(Principal Investigator) 관점의 비판적 피드백 보고서를 자동으로 생성합니다.
- **유연한 LLM 지원**: `LiteLLM`을 통해 OpenAI, Gemini, Perplexity 등 다양한 LLM을 설정 파일 변경만으로 손쉽게 교체하며 사용할 수 있습니다.
- **강력한 설정 관리**: `Hydra`를 사용하여 모델, 프롬프트, 입출력 경로 등 모든 설정을 체계적으로 관리하고 커맨드 라인에서 쉽게 변경할 수 있습니다. 특히 `mode` YAML 파일을 통해 분석 모드별로 최적화된 설정을 일괄 적용할 수 있습니다.

## 3. 설치 및 설정

### 3.1. Conda 가상환경 생성 및 활성화
```bash
conda create -n critical-analyzer python=3.10 -y
conda activate critical-analyzer
```

### 3.2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 3.3. API 키 설정
프로젝트 루트에 `.env` 파일을 생성하고 사용하는 LLM의 API 키를 입력합니다.
```dotenv
# .env
OPENAI_API_KEY="sk-..."
GEMINI_API_KEY="..."
PERPLEXITY_API_KEY="..."
```

### 3.4. 분석 폴더 및 모드 설정
`configs/config.yaml` 파일은 기본 설정을 담당하며, `configs/mode/` 폴더 내의 YAML 파일들이 각 분석 모드에 특화된 설정을 정의합니다.

**`configs/config.yaml` 예시**:
```yaml
defaults:
  - llm: gemini_flash
  - mode: integration # 기본 분석 모드 설정 (integration 또는 summary)
  - _self_

base_output_dir: "/home/joon/dev/critical_analyzer/outputs" # 모든 결과 파일이 저장될 기본 출력 디렉토리
summaries_sub_dir: "summaries" # 개별 요약 파일이 저장될 하위 디렉토리
output_file: "comprehensive_report.md"
# ... (기타 Hydra 설정)

prompt:
  individual_summary_prompt: "prompts/individual_summary.txt" # 개별 문서 요약 프롬프트
```

**`configs/mode/integration.yaml` 예시 (문서 통합 모드)**:
```yaml
analysis_mode: "integration"
input_dirs:
  - "/home/joon/dev/critical_analyzer/data/Presentation" # 통합할 첫 번째 폴더
  - "/home/joon/dev/critical_analyzer/data/Proposal"     # 통합할 두 번째 폴더
final_prompt_path: "prompts/document_integration.txt" # 문서 통합에 사용할 프롬프트
feedback_prompt_path: "prompts/feedback.txt"         # 피드백 생성에 사용할 프롬프트 (선택 사항)
```

**`configs/mode/summary.yaml` 예시 (요약 분석 모드)**:
```yaml
analysis_mode: "summary"
input_dirs:
  - "/home/joon/dev/critical_analyzer/sample_docs" # 요약 분석할 폴더
final_prompt_path: "prompts/comprehensive_analysis.txt" # 종합 분석에 사용할 프롬프트
feedback_prompt_path: "prompts/feedback.txt"         # 피드백 생성에 사용할 프롬프트 (선택 사항)
```

## 4. 실행 방법

프로젝트 루트 디렉토리에서 `main.py`를 실행합니다. `mode` 파라미터를 통해 원하는 분석 모드를 지정할 수 있습니다.

### 4.1. 문서 통합 모드 실행 (Integration Mode)
여러 버전의 초안 문서들을 통합하여 하나의 최적화된 문서를 생성합니다. `configs/mode/integration.yaml`에 정의된 `input_dirs`의 모든 폴더를 순회하며 통합 작업을 수행합니다.
```bash
python src/main.py mode=integration
```

### 4.2. 요약 분석 모드 실행 (Summary Mode)
개별 문서들을 분석하고 요약하여 종합 보고서를 생성합니다. `configs/mode/summary.yaml`에 정의된 `input_dirs`의 모든 폴더를 순회하며 요약 작업을 수행합니다.
```bash
python src/main.py mode=summary
```

### 4.3. 다른 LLM 모델로 실행하기
커맨드 라인에서 `llm` 설정을 변경하여 다른 모델로 분석을 실행할 수 있습니다. `configs/llm` 폴더에 있는 파일명을 사용합니다.
```bash
# gpt-4o-mini 모델로 실행 (통합 모드)
python src/main.py mode=integration llm=openai_4o_mini

# Perplexity Sonar 모델로 실행 (요약 모드)
python src/main.py mode=summary llm=perplexity_sonar
```

## 5. 출력 구조

분석 결과는 각 `input_dir` 내부에 `outputs/` 폴더가 생성되어 저장됩니다. 각 `outputs/` 폴더 안에는 `summaries/` 폴더와 최종 보고서 파일이 포함됩니다.

**경로 예시**: `/home/joon/dev/critical_analyzer/data/Presentation/outputs/`

```
[input_dir]/
└── outputs/
    ├── summaries/                          <-- 📄 개별 분석 보고서 폴더 (요약 모드에서 생성)
    │   ├── doc1_summary.md
    │   ├── doc2_summary.md
    │   └── ...
    ├── 250716_gemini_gemini-2.5-flash_Presentation_integrated_1.md  <-- ✨ 통합 모드 최종 문서 (파일명에 폴더명과 모드명 포함)
    ├── 250716_gemini_gemini-2.5-flash_Presentation_integrated_1_feedback.md <-- ✨ 통합 모드 피드백 보고서
    └── .hydra/                             <-- Hydra 설정 및 로그
```

- **`summaries/`**: 각 문서에 대한 개별 분석 보고서가 저장되는 폴더입니다. 원본 파일명에 `_summary.md`가 붙은 형태로 저장됩니다.
- **최종 보고서**: `[날짜]_[LLM모델명]_[입력폴더명]_[모드명]_[숫자].md` 형식으로 저장됩니다. (예: `250716_gemini_gemini-2.5-flash_Presentation_integrated_1.md`)
- **피드백 보고서**: 최종 보고서 파일명 뒤에 `_feedback.md`가 붙은 형태로 저장됩니다.



## 6. Report Mode - 학생-AI 튜터 대화 분석 시스템

### 6.1. 개요
Critical Analyzer는 학생과 AI 튜터 간의 대화 데이터를 분석하여 학생용 격려 보고서와 교사용 학습 분석 보고서를 자동 생성하는 Report Mode를 제공합니다.

### 6.2. 기능
- **학생 보고서**: 긍정적 피드백과 격려 중심의 개인별 보고서
- **교사 보고서**: 학습 패턴 분석과 교육적 권장사항이 포함된 전문 보고서
- **다중 형식 출력**: 마크다운, HTML, PDF 형식으로 동시 생성
- **수식 지원**: MathJax를 통한 LaTeX 수식 완벽 렌더링
- **배치 처리**: 대용량 데이터 자동 처리 및 진행 상황 모니터링

### 6.3. 실행 방법
```bash
# Report Mode 실행
python src/main.py mode=report

# 배치 처리 상태 확인
python batch_status.py

# 빠른 상태 확인
python quick_status.py

# 연속 모니터링 (10초마다 업데이트)
python batch_status.py --monitor
```

### 6.4. 출력 구조
```
outputs/reports/
├── student/                    # 학생용 보고서
│   ├── 학생_20101.md
│   ├── 학생_20101.html
│   ├── 학생_20101.pdf
│   └── ...
└── teacher/                    # 교사용 보고서
    ├── 학생_20101.md
    ├── 학생_20101.html
    ├── 학생_20101.pdf
    └── ...
```

### 6.5. 배치 처리 모니터링
Report Mode는 대용량 데이터를 효율적으로 처리하기 위한 다양한 모니터링 도구를 제공합니다:

#### 빠른 상태 확인
```bash
python quick_status.py
```

#### 상세 모니터링
```bash
python batch_status.py
```

#### 연속 모니터링
```bash
python batch_status.py --monitor
```

#### 수동 명령어들
```bash
# 진행률 계산
echo "scale=1; $(find outputs/reports -name '*.md' | wc -l) / 2 / 41 * 100" | bc

# 현재 처리 중인 학생 확인
tail -20 logs/batch_report_*.log | grep "Processing:"

# 실시간 로그 확인
tail -f logs/batch_report_*.log

# 완료된 파일 수 확인
find outputs/reports -name "*.md" | wc -l
```

### 6.6. PDF 생성
HTML 파일에서 PDF로 변환하는 방법:
1. 브라우저에서 HTML 파일 열기
2. Ctrl+P (또는 Cmd+P) 누르기
3. 대상을 "PDF로 저장" 선택
4. 여백을 "최소"로 설정
5. 배경 그래픽 인쇄 활성화
6. 저장 클릭

또는 자동 PDF 생성:
```bash
python src/pdf_generator.py
```

## 7. 시스템 요구사항

### 7.1. 의존성 설치
```bash
# 기본 의존성
pip install -r requirements.txt

# PDF 생성을 위한 추가 도구 (선택사항)
sudo apt-get install pandoc texlive-xetex texlive-fonts-recommended
```