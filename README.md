# Critical Analyzer

## 1. 프로젝트 개요

**Critical Analyzer**는 지정된 폴더 내의 마크다운 문서들을 LLM을 활용하여 심층 분석하고, 세계 최고 수준의 학술지 기준에 입각한 비판적 평가 보고서를 생성하는 파이썬 애플리케이션입니다.

단순 요약을 넘어, 다수의 전문가 페르소나(LLM as a Judge)를 통해 각 문서를 개별적으로 평가하고, 이를 종합하여 전체적인 맥락(Big Picture)을 분석합니다.

## 2. 주요 특징

- **전문가 수준의 비판적 분석**: 탑티어 학술지 편집위원회의 엄격한 기준을 모방한 프롬프트를 통해 연구의 방법론, 이론적 기여도, 실용성을 심층적으로 평가합니다.
- **2단계 분석 프로세스**:
    1.  **개별 분석**: 각 문서를 독립적으로 분석하여 상세한 평가 보고서를 개별 파일로 저장합니다.
    2.  **종합 분석**: 생성된 모든 개별 보고서를 종합하여 전체 컬렉션에 대한 '빅 픽처'와 핵심 테마를 도출합니다.
- **유연한 LLM 지원**: `LiteLLM`을 통해 OpenAI, Gemini, Perplexity 등 다양한 LLM을 설정 파일 변경만으�� 손쉽게 교체하며 사용할 수 있습니다.
- **강력한 설정 관리**: `Hydra`를 사용하여 모델, 프롬프트, 입출력 경로 등 모든 설정을 체계적으로 관리하고 커맨드 라인에서 쉽게 변경할 수 있습니다.

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

### 3.4. 분석 폴더 지정
`configs/config.yaml` 파일을 열어 `input_dir` 값을 분석하고 싶은 폴더의 **절대 경로**로 수정합니다.
```yaml
# configs/config.yaml
input_dir: "/home/user/Documents/MyResearch"
```

## 4. 실행 방법

### 4.1. 기본 실행
프로젝트 루트 디렉토리에서 아래 명령어를 실행합니다.
```bash
python src/main.py
```

### 4.2. 다른 모델로 실행하기
커맨드 라인에서 `llm` 설정을 변경하여 다른 모델로 분석을 실행할 수 있습니다. `configs/llm` 폴더에 있는 파일명을 사용합니다.
```bash
# gpt-4o-mini 모델로 실행
python src/main.py llm=openai_4o_mini

# Perplexity Sonar 모델로 실행
python src/main.py llm=perplexity_sonar_large
```

## 5. 출력 구조

실행이 완료되면 `outputs/` 폴더 아래에 날짜와 시간으로 된 폴더가 생성됩니다. 최종 결과물은 이 폴더 안에 저장됩니다.

**경로 예시**: `outputs/2025-07-10/10-30-00/`

```
outputs/
└── 2025-07-10/
    └── 10-30-00/
        ├── summaries/                          <-- 📄 개별 분석 보고서 폴더
        │   ├── doc1_summary.md
        │   ├── doc2_summary.md
        │   └── ...
        ├── comprehensive_report.md             <-- ✨ 최종 종합 분석 보고서
        └── .hydra/                             <-- Hydra 설정 및 로그
```

- **`summaries/`**: 각 문서에 대한 개별 분석 보고서가 저장되는 폴더입니다. 원본 파일명에 `_summary.md`가 붙은 형태로 저장됩니다.
- **`comprehensive_report.md`**: 저장된 모든 개별 분석 보고서들을 종합하여 생성된 최종 보고서입니다.