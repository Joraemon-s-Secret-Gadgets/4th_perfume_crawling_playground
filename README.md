# SKN26 Project: Perfume Crawling & Database

SKN26 4기 프로젝트를 위한 향수 데이터 크롤링 및 관리 저장소입니다.

## Structure

```text
.
├── .github/
├── data/               <-- 크롤링된 최종 데이터 (Bvlgari, Chanel, Dior)
├── scripts/            <-- 데이터 수집 및 가공 스크립트
│   ├── 01_crawl_urls/
│   ├── 02_crawl_details/
│   ├── 03_refine_data/
│   ├── 04_extract_keywords/
│   ├── 05_translate_to_korean_keywords/
│   └── 06_formatting/
├── requirements.txt    <-- 프로젝트 의존성 라이브러리
└── README.md
```

## Data Overview

현재 수집된 브랜드 및 향수 데이터 개수는 다음과 같습니다:

| Brand | Count |
| :--- | :--- |
| **Bvlgari** | 61 |
| **Chanel** | 83 |
| **Dior** | 126 |
| **Total** | **270** |

## Directory Guide

- `scripts/`: 향수 데이터 크롤링, 상세 정보 추출, 키워드 추출, 번역 및 포맷팅 스크립트 모음
- `data/`: 크롤링 프로세스를 통해 생성된 최종 향수 데이터 (JSON)

## Crawling Strategy

본 프로젝트는 다음과 같은 단계로 데이터를 수집 및 가공합니다:

1. **URL 수집 (`01_crawl_urls`)**: 브랜드별 공식 홈페이지 또는 향수 전문 사이트에서 제품 목록의 URL을 수집합니다.
2. **상세 정보 추출 (`02_crawl_details`)**: 수집된 URL에 접속하여 Playwright를 이용해 향수 노트(Top, Heart, Base), 메인 어코드, 가격, 이미지 등의 상세 정보를 스크래핑합니다.
3. **데이터 정제 (`03_refine_data`)**: 중복 데이터를 제거하고, 불필요한 텍스트를 정리하여 데이터를 표준화합니다.
4. **키워드 추출 (`04_extract_keywords`)**: OpenAI API(GPT)를 활용하여 향수의 설명과 노트를 분석하고, 분위기(Mood), 어울리는 상황(Occasion) 등의 키워드를 추출합니다.
5. **한글 번역 및 매핑 (`05_translate_to_korean_keywords`)**: 영문으로 수집된 어코드와 노트들을 미리 정의된 사전(Mapping)과 LLM을 활용하여 자연스러운 한글로 번역합니다.
6. **최종 포맷팅 (`06_formatting`)**: 데이터베이스 삽입에 최적화된 최종 JSON 포맷으로 변환합니다.

## Getting Started

### 1. 의존성 설치
```bash
pip install -r requirements.txt
playwright install
```

### 2. 크롤링 스크립트 실행
스크립트는 순차적으로 실행되도록 구성되어 있습니다. 각 디렉토리 내의 파이썬 스크립트를 순서대로 실행하세요.

## Tech Stack
- **Crawling**: Playwright, BeautifulSoup4
- **AI/LLM**: OpenAI (LangChain)
- **Data**: JSON

## License
See [LICENSE](./LICENSE).
