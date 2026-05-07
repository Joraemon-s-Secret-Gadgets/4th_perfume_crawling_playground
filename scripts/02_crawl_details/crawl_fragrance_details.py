import asyncio
import random
import json
import re
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup


async def get_perfume_and_review(page, url, brand_name):
    """상세 정보 + 리뷰 수집 (각 항목에 브랜드 이름 포함)"""
    data = {
        "brand": brand_name,  # <--- 요청하신 브랜드 필드 추가
        "url": url,
        "image_url": "N/A",
        "main_accords": [],
        "notes": {"Top": [], "Heart": [], "Base": []},
        "usage_stats": {},
        "first_impression": "N/A",
        "scent_profile": "N/A",
        "status": "Success",
    }

    try:
        # --- 1단계: 상세 페이지 접속 ---
        response = await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(3)

        content = await page.content()
        if response.status >= 400 or "Worker Limit" in content or "1011" in content:
            print(f"⚠️ 상세 페이지 리밋 감지 - {url} 스킵")
            return None

        soup = BeautifulSoup(content, "html.parser")

        # 이미지 주소
        img_tag = soup.select_one(".perfume-img-bg img")
        data["image_url"] = img_tag.get("src") if img_tag else "N/A"

        # Main Accords
        acc_h = soup.find(lambda t: t.name in ["h2", "h3"] and "Main Accords" in t.text)
        if acc_h:
            container = acc_h.find_next("div")
            for a in container.find_all("a", class_="group"):
                n, v = a.find("span", class_="w-24"), a.find(
                    "span", class_="tabular-nums"
                )
                if n and v:
                    data["main_accords"].append(
                        {"accord": n.text.strip(), "percentage": v.text.strip()}
                    )

        # 모든 노트
        note_map = {"Top": "Top Notes", "Heart": "Heart Notes", "Base": "Base Notes"}
        for key, label in note_map.items():
            s = soup.find("span", string=lambda x: x and label in x)
            if s:
                lst = s.find_parent("div").find_next_sibling("div")
                if lst:
                    data["notes"][key] = [
                        n.text.strip() for n in lst.select("span.flex-1")
                    ]

        # Usage Stats
        s_h = soup.find(lambda t: "Best Season" in t.text)
        if s_h:
            s_d = s_h.find_next("div", class_="grid-cols-4")
            data["usage_stats"]["Season"] = dict(
                zip(
                    ["Winter", "Spring", "Summer", "Fall"],
                    [p.text.strip() for p in s_d.find_all("p", class_="font-semibold")],
                )
            )

        t_h = soup.find(lambda t: "Day & Night" in t.text)
        if t_h:
            t_d = t_h.find_next("div", class_="grid-cols-2")
            data["usage_stats"]["Time"] = dict(
                zip(
                    ["Day", "Night"],
                    [p.text.strip() for p in t_d.find_all("p", class_="font-semibold")],
                )
            )

        # --- 2단계: 리뷰 페이지 접속 ---
        review_url = url.replace("/perfume/", "/reviews/")
        r_response = await page.goto(
            review_url, wait_until="domcontentloaded", timeout=60000
        )
        await asyncio.sleep(5)

        r_content = await page.content()
        if r_response.status >= 400 or "Worker Limit" in r_content:
            data["status"] = "Review Skipped (Limit)"
            return data

        r_soup = BeautifulSoup(r_content, "html.parser")

        # First Impression (멀티 문단)
        fi_h = r_soup.find(
            lambda t: t.name in ["h2", "h3"]
            and re.search(r"First Impression", t.get_text(), re.I)
        )
        if fi_h:
            paras = []
            curr = fi_h.find_next_sibling()
            while curr and curr.name == "p":
                paras.append(curr.get_text(strip=True).replace("''", "'"))
                curr = curr.find_next_sibling()
            data["first_impression"] = "\n".join(paras)

        # Scent Profile (멀티 문단)
        sp_h = r_soup.find(
            lambda t: t.name in ["h2", "h3"]
            and re.search(r"Scent Profile", t.get_text(), re.I)
        )
        if sp_h:
            paras = []
            curr = sp_h.find_next_sibling()
            while curr and curr.name == "p":
                paras.append(curr.get_text(strip=True).replace("''", "'"))
                curr = curr.find_next_sibling()
            data["scent_profile"] = "\n".join(paras)

        return data

    except Exception as e:
        print(f"❌ 오류 발생 ({url}): {e}")
        return None


async def run_final_crawler():
    brand_tasks = [
        {"name": "Bvlgari", "file": "bvlgari_links.json"},
        {"name": "Dior", "file": "Dior_links.json"},
    ]

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)  # Headless 모드
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        )
        page = await context.new_page()

        for brand in brand_tasks:
            brand_name = brand["name"]
            print(f"\n🌟 [{brand_name.upper()}] 시작...")

            try:
                with open(brand["file"], "r", encoding="utf-8") as f:
                    urls = json.load(f).get("links", [])
            except FileNotFoundError:
                continue

            results = []
            for i, url in enumerate(urls):
                if "goto" in url:
                    continue

                print(f"🔄 [{brand_name}] {i+1}/{len(urls)}: {url}")
                # brand_name을 인자로 전달합니다.
                res = await get_perfume_and_review(page, url, brand_name)

                if res:
                    results.append(res)

                # 10개 제품마다 10~15초 랜덤 휴식
                if (i + 1) % 10 == 0:
                    cooldown = random.uniform(10, 15)
                    print(f"😴 리밋 방지 휴식 ({cooldown:.2f}초)...")
                    await asyncio.sleep(cooldown)
                else:
                    await asyncio.sleep(random.uniform(2, 4))

                if len(results) % 5 == 0:
                    with open(
                        f"{brand_name}_data_partial.json", "w", encoding="utf-8"
                    ) as f:
                        json.dump(results, f, ensure_ascii=False, indent=4)

            with open(f"{brand_name}_final_data.json", "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=4)

            print(f"✅ {brand_name} 완료!")

        await browser.close()
        print("\n✨ 모든 작업이 종료되었습니다.")


if __name__ == "__main__":
    asyncio.run(run_final_crawler())
