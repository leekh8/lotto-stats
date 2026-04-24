# lotto-stats

로또 6/45·연금복권720 당첨번호 통계 분석 및 ML 예측 실험

> "할 수 없다는 것을 실험으로 증명하는 것도 엄연한 데이터 사이언스다."

## 프로젝트 구조

```
lotto-stats/
├── src/
│   ├── crawl_lotto.py       # 로또 6/45 전회차 수집 (동행복권 API)
│   └── crawl_pension.py     # 연금복권720 전회차 수집
└── notebooks/
    ├── 01_lotto_stats.ipynb     # Phase 1: 통계 시각화
    ├── 02_pension_stats.ipynb   # Phase 1: 연금복권 통계
    └── 03_ml_experiment.ipynb  # Phase 2: ML 예측 실험
```

## Phase 1 — 통계 분석

동행복권 API로 수집한 전회차 데이터를 바탕으로 다양한 통계를 시각화합니다.

| 분석 항목 | 내용 |
|-----------|------|
| 번호별 출현 빈도 | 핫(상위 25%)·콜드(하위 25%) 번호 구분 |
| 합계 분포 | 6개 번호 합계의 분포 및 평균 |
| 홀짝 분포 | 홀수·짝수 번호 개수 비율 |
| 구간 분포 | 1~10 / 11~20 / 21~30 / 31~40 / 41~45 |
| 동반 출현 히트맵 | 두 번호가 함께 나온 횟수 45×45 매트릭스 |

## Phase 2 — ML 예측 실험

**가설:** 과거 당첨번호 패턴으로 미래 번호를 예측할 수 있는가?

세 가지 모델을 비교합니다.

| 모델 | 설명 |
|------|------|
| Random (baseline) | 1~45에서 무작위 6개 선택 |
| Frequency | 훈련셋 출현 빈도 상위 6번호 고정 선택 |
| LSTM | 직전 10회차를 멀티-핫 인코딩 후 시퀀스 학습 |

**평가 지표:** 실제 당첨번호와 겹치는 개수의 평균  
**이론 기댓값 (완전 랜덤):** ≈ 0.8개

### 결론

세 모델 모두 평균 일치 수가 이론 기댓값에 수렴하며, LSTM도 랜덤 베이스라인을 유의미하게 초과하지 못합니다.

로또 추첨은 **IID(독립 동일 분포)** 사건으로, 각 회차가 완전히 독립적입니다. 시계열 모델은 자기상관(autocorrelation)이 있는 데이터에만 유효하며, 로또에는 그러한 패턴이 존재하지 않습니다.

## 시작하기

```bash
# 의존성 설치
pip install pandas requests matplotlib seaborn tensorflow

# 데이터 수집
python src/crawl_lotto.py      # data/lotto.csv 생성 (~10분)
python src/crawl_pension.py    # data/pension720.csv 생성

# 노트북 실행
jupyter notebook notebooks/
```

데이터 파일(`data/*.csv`)은 `.gitignore`에 포함되어 있으므로 직접 수집해야 합니다.  
이후 실행 시 마지막 회차 이후 데이터만 증분 수집합니다.

## 데이터 출처

[동행복권](https://www.dhlottery.co.kr) 공개 API
