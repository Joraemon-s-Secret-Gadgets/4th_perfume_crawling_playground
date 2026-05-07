import asyncio
import json
import random
import re
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup


async def test_full_extraction(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        )
        page = await context.new_page()

        # 1. 상세 페이지 수집 (이전과 동일)
        print(f"🚀 [1단계] 상세 페이지 접속: {url}")
        await page.goto(url, wait_until="domcontentloaded")
        await asyncio.sleep(3)
        content = await page.content()
        soup = BeautifulSoup(content, "html.parser")

        # 이미지 주소
        img_tag = soup.select_one(".perfume-img-bg img")
        image_url = img_tag.get("src") if img_tag else "N/A"

        # 모든 노트 추출
        all_notes = {"Top": [], "Heart": [], "Base": []}
        note_map = {"Top": "Top Notes", "Heart": "Heart Notes", "Base": "Base Notes"}
        for key, label in note_map.items():
            s = soup.find("span", string=lambda x: x and label in x)
            if s:
                lst = s.find_parent("div").find_next_sibling("div")
                if lst:
                    all_notes[key] = [n.text.strip() for n in lst.select("span.flex-1")]

        # 2. 리뷰 페이지 수집 (보정된 로직)
        review_url = url.replace("/perfume/", "/reviews/")
        print(f"🚀 [2단계] 리뷰 페이지 접속: {review_url}")
        await page.goto(review_url, wait_until="domcontentloaded")
        await asyncio.sleep(5)  # 리뷰 본문 렌더링을 위해 충분히 대기

        r_content = await page.content()
        r_soup = BeautifulSoup(r_content, "html.parser")

        first_impression = "N/A"
        scent_profile = "N/A"

        # 텍스트 정규식 검색 (대소문자 무시, 부분 일치)
        # 'First Impression' 혹은 'First Impressions' 모두 잡음
        fi_header = r_soup.find(
            lambda t: t.name in ["h2", "h3"]
            and re.search(r"First Impression", t.get_text(), re.I)
        )
        if fi_header:
            paras = []
            curr = fi_header.find_next_sibling()
            # 다음 h2 헤더를 만나기 전까지의 모든 p 태그 수집
            while curr and curr.name == "p":
                paras.append(
                    curr.get_text(strip=True).replace("''", "'")
                )  # 중복 따옴표 정제
                curr = curr.find_next_sibling()
            first_impression = "\n".join(paras)

        # 'Scent Profile' 검색
        sp_header = r_soup.find(
            lambda t: t.name in ["h2", "h3"]
            and re.search(r"Scent Profile", t.get_text(), re.I)
        )
        if sp_header:
            paras = []
            curr = sp_header.find_next_sibling()
            while curr and curr.name == "p":
                paras.append(curr.get_text(strip=True).replace("''", "'"))
                curr = curr.find_next_sibling()
            scent_profile = "\n".join(paras)

        # 결과 리포트
        report = {
            "url": url,
            "image_url": image_url,
            "all_notes": all_notes,
            "reviews": {
                "first_impression": first_impression,
                "scent_profile": scent_profile,
            },
        }

        print("\n" + "✨" * 40)
        print(json.dumps(report, indent=4, ensure_ascii=False))
        print("✨" * 40)

        await browser.close()


if __name__ == "__main__":
    # 방금 주신 소스의 대상인 Bvlgari Omnia Pink Sapphire로 테스트
    test_url = "https://fraganty.ai/perfume/omnia-pink-sapphire"
    asyncio.run(test_full_extraction(test_url))
