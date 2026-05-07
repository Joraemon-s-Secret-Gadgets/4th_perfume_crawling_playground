import asyncio
import json
import os
from typing import List, Optional
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

# .env 파일에서 API 키 로드
load_dotenv()


# ==========================================
# 1. 구조화된 출력 규격 (Pydantic Model)
# ==========================================
class MultiLangItem(BaseModel):
    en: str = Field(
        ...,
        description="English term representing the concept (e.g., 'Fresh', 'Bergamot')",
    )
    ko: str = Field(
        ...,
        description="영문 용어에 대응하는 자연스러운 한국어 표현 (예: '상쾌한', '베르가못')",
    )


class PerfumeAnalysis(BaseModel):
    moods: List[MultiLangItem] = Field(
        min_length=5,
        max_length=8,
        description="향수가 전달하는 감성적 분위기와 이미지 (예: Elegant, Energetic, Mysterious, Sophisticated, Radiant)",
    )
    occasions: List[MultiLangItem] = Field(
        min_length=3,
        max_length=6,
        description="이 향수가 가장 잘 어울리는 구체적인 상황, 장소 또는 계절 (예: Spring, Date Night, Office, Formal Events)",
    )
    gender_profile: MultiLangItem = Field(
        ...,
        description="향수의 성별 지향성. Masculine(남성적), Feminine(여성적), Unisex(공용) 중 가장 적합한 것 선택",
    )
    strength_score: int = Field(
        ...,
        ge=1,
        le=5,
        description="향의 전반적인 강도 및 발산력 (1: 피부에 밀착되는 은은함 ~ 5: 공간을 압도하는 강력한 존재감)",
    )
    reasoning: str = Field(
        ...,
        description="제시된 첫인상, 향 프로파일, 노트 정보를 바탕으로 위 분석 결과를 도출한 상세한 논리적 근거 (한국어로 작성, 100자 미만)",
    )


# ==========================================
# 2. AI 분석 엔진
# ==========================================
class PerfumeEnricher:
    def __init__(self):
        # GPT-4o-mini 모델 사용 (구조화된 출력 강제)
        self.llm = ChatOpenAI(
            model="gpt-4o-mini", temperature=0.2  # 정확도를 위해 낮은 온도로 설정
        ).with_structured_output(PerfumeAnalysis)

        # 구체화된 통합 분석 프롬프트
        self.analysis_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """당신은 세계적인 향수 비평가이자 조향사인 '마스터 퍼퓨머'입니다. 
제공된 향수 데이터를 바탕으로 다각적인 분석을 수행하여 핵심 분위기와 이미지를 추출하는 것이 임무입니다.

분석 가이드라인:
1. **Moods (최소 5개)**: 단순히 향료의 느낌을 넘어, 이 향수를 뿌렸을 때 연상되는 심리적 상태나 사회적 이미지를 포착하세요. 매우 풍부하고 구체적인 키워드를 선별하세요.
2. **Occasions (최소 3개)**: 'Usage Stats'의 계절/시간대 정보와 향의 무게감을 결합하여 최적의 추천 상황(장소, 활동, 복장 등)을 구체적으로 도출하세요.
3. **Bilingual**: 모든 영문 용어는 해당 분야에서 통용되는 정확한 표현을 사용하고, 한국어 대응어는 한국 향수 사용자들에게 친숙하고 자연스러운 단어를 선택하세요.
4. **Consistency**: 모든 분석 결과는 서로 논리적으로 일관성이 있어야 하며, 'Reasoning' 필드에 그 인과관계를 명확히 설명하세요.""",
                ),
                (
                    "user",
                    """다음 향수 데이터를 심층 분석해 주세요:

[향수 정보]
- 브랜드: {brand}
- 이름: {name}
- 메인 어코드: {accords}
- 향료 노트: {notes}
- 계절감/시간대: {usage}

[설명글]
- 첫인상: {first_impression}
- 상세 프로파일: {scent_profile}

위 데이터를 바탕으로 지정된 스키마에 맞춰 분석 결과를 반환해 주세요.""",
                ),
            ]
        )

    async def enrich(self, item: dict, max_retries: int = 3):
        # 데이터 구성
        input_data = {
            "brand": item.get("brand"),
            "name": item.get("name"),
            "accords": ", ".join(item.get("main_accords", [])),
            "notes": json.dumps(item.get("notes", {}), ensure_ascii=False),
            "usage": f"Seasons: {item.get('usage_stats', {}).get('Season')}, Time: {item.get('usage_stats', {}).get('Time')}",
            "first_impression": item.get("first_impression"),
            "scent_profile": item.get("scent_profile"),
        }

        for attempt in range(max_retries):
            try:
                # invoke는 동기 메서드이므로 run_in_executor 등을 사용하는 것이 좋으나,
                # 현재는 단순 루프 내에서 처리하며 재시도 로직을 추가함
                chain = self.analysis_prompt | self.llm
                analysis = chain.invoke(input_data)
                item["ai_analysis"] = analysis.model_dump()
                print(f"✅ 분석 성공: {item.get('name')}")
                return item
            except Exception as e:
                wait_time = (attempt + 1) * 2  # 점진적 대기 시간 증가 (2s, 4s, 6s)
                print(
                    f"⚠️ 분석 시도 중 오류 ({item.get('name')}) [{attempt + 1}/{max_retries}]: {e}"
                )
                if attempt < max_retries - 1:
                    print(f"⏳ {wait_time}초 후 재시도합니다...")
                    await asyncio.sleep(wait_time)
                else:
                    print(f"❌ 최종 분석 실패 ({item.get('name')})")
                    item["ai_analysis"] = None

        return item


# ==========================================
# 3. 메인 프로세서
# ==========================================
async def process_all_refined_files(file_list: List[str]):
    enricher = PerfumeEnricher()

    for input_file in file_list:
        output_file = input_file.replace(".json", "_enriched.json")

        if not os.path.exists(input_file):
            print(f"⚠️ 파일을 찾을 수 없습니다: {input_file}")
            continue

        print(f"\n🚀 {input_file} 분석 시작")

        with open(input_file, "r", encoding="utf-8") as f:
            perfumes = json.load(f)

        enriched_results = []
        # 대량 데이터 처리를 위해 순차적으로 처리 (필요시 세마포어로 동시성 제어 가능)
        for i, perfume in enumerate(perfumes):
            enriched_item = await enricher.enrich(perfume)
            enriched_results.append(enriched_item)

            # 10개마다 중간 저장 (안정성 확보)
            if (i + 1) % 10 == 0:
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(enriched_results, f, ensure_ascii=False, indent=4)
                print(f"📝 중간 저장 완료 ({i + 1}/{len(perfumes)})")

            # API 레이트 리미트 보호를 위한 짧은 휴식
            await asyncio.sleep(0.3)

        # 최종 저장
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(enriched_results, f, ensure_ascii=False, indent=4)

        print(f"💾 {input_file} 가공 완료 및 저장: {output_file}")


# ==========================================
# 4. 실행부
# ==========================================
if __name__ == "__main__":
    target_files = ["Bvlgari_final_data_refined.json", "Dior_final_data_refined.json"]

    # 전체 프로세스 실행
    asyncio.run(process_all_refined_files(target_files))
