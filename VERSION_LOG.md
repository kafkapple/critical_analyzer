# Critical Analyzer - 버전 로그 및 실험 기록

## 📋 버전 관리 시스템

### Summary 모드 버전 비교

| 버전 | 파일명 | 주요 특징 | 사용 목적 |
|------|--------|-----------|----------|
| **v1.0** | `summary.yaml` | 기본 심화 분석 | 표준 연구 분석 |
| **v2.0** | `summary_v2.yaml` | 토큰 최적화 + 개별 요약 | 대용량 문서 처리 |

---

## 🔍 Summary 모드 세부 비교

### **v1.0 (기본 버전)**
- **설정 파일**: `configs/mode/summary.yaml`
- **개별 프롬프트**: `prompts/summary/individual_summary.txt` (136줄)
- **종합 프롬프트**: `prompts/summary/comprehensive_analysis.txt`
- **특징**: 
  - 상세한 3단계 심화 분석
  - Deep Mode 기본 실행
  - 체계적 평가 루브릭 포함
- **용도**: 소규모 문서 집합, 심화 분석 필요시

### **v2.0 (최적화 버전)**
- **설정 파일**: `configs/mode/summary_v2.yaml`
- **개별 프롬프트**: `prompts/summary/individual_summary_compact.txt` (45줄)
- **종합 프롬프트**: `prompts/summary/comprehensive_analysis_v2.txt`
- **특징**:
  - 토큰 효율성 극대화
  - 개별 문서 요약 섹션 포함
  - Compact 모드 적용
- **용도**: 대용량 문서 처리, 토큰 제한 환경

---

## 🧪 실험 일관성 가이드

### **버전 선택 기준**

1. **문서 수 < 10개**: v1.0 권장
2. **문서 수 10-30개**: v2.0 권장
3. **토큰 오류 발생**: v2.0 강제 사용
4. **심화 분석 필요**: v1.0 선택

### **실험 설정 방법**

```bash
# v1.0 사용 (기본)
# configs/config.yaml에서:
- mode: summary

# v2.0 사용 (최적화)
# configs/config.yaml에서:
- mode: summary_v2
```

### **LLM 설정 옵션**

```yaml
# 기본 설정
- llm: gemini_flash

# 최적화 설정 (v2.0 권장)
- llm: gemini_flash_optimized
```

---

## 📊 성능 비교 (예상)

| 항목 | v1.0 | v2.0 |
|------|------|------|
| 토큰 사용량 | 높음 | 낮음 |
| 처리 속도 | 보통 | 빠름 |
| 분석 깊이 | 상세 | 간결 |
| 오류 발생률 | 높음 | 낮음 |

---

## 🔄 향후 버전 계획

### **v3.0 (계획)**
- 적응형 프롬프트 길이 조절
- 모델별 최적화 설정
- 자동 버전 선택 기능

---

## 📝 실험 기록 템플릿

### 실험 진행 시 다음 정보 기록:
- **날짜**: 
- **버전**: (v1.0 / v2.0)
- **문서 수**: 
- **LLM 설정**: 
- **결과**: (성공/실패/오류)
- **특이사항**: 

---

*최종 업데이트: 2025-07-16*