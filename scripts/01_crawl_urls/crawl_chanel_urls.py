import asyncio
import random
import json
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

async def crawl_chanel_links():
    # Chanel has 6 pages
    brand_name = "Chanel"
    total_pages = 6
    base_url = "https://fraganty.ai"
    target_url = f"{base_url}/brands/{brand_name}"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        all_links = []
        print(f"\n🚀 [{brand_name.upper()}] 링크 수집 시작...")

        await page.goto(target_url)

        for current_page in range(1, total_pages + 1):
            print(f"--- {brand_name} : {current_page} / {total_pages} 페이지 수집 중 ---")

            # 페이지 로딩 대기
            await asyncio.sleep(random.uniform(2.5, 4.0))

            content = await page.content()
            soup = BeautifulSoup(content, "html.parser")

            items = soup.find_all("a", class_="group block")
            current_page_count = 0

            for item in items:
                href = item.get("href")
                if href:
                    if "goto" in href:
                        continue

                    full_link = f"{base_url}{href}" if href.startswith("/") else href

                    if full_link not in all_links:
                        all_links.append(full_link)
                        current_page_count += 1

            print(f"> {current_page}페이지에서 {current_page_count}개 추출 완료 (누적: {len(all_links)}개)")

            if current_page < total_pages:
                next_button = page.get_by_role("button", name="Next").or_(
                    page.get_by_role("link", name="Next")
                )

                if await next_button.is_visible():
                    await asyncio.sleep(random.uniform(1.0, 2.0))

                    first_item_el = page.locator(".group.block").first
                    if await first_item_el.count() > 0:
                        first_item_before = await first_item_el.inner_text()
                        await next_button.click()

                        try:
                            await page.wait_for_function(
                                f"document.querySelector('.group.block').innerText !== `{first_item_before}`",
                                timeout=5000,
                            )
                        except:
                            await asyncio.sleep(3)
                    else:
                        await next_button.click()
                        await asyncio.sleep(3)
                else:
                    print("! Next 버튼을 더 이상 찾을 수 없어 종료합니다.")
                    break

        output_data = {
            "brand": brand_name,
            "total_count": len(all_links),
            "links": all_links,
        }

        file_name = f"raw/{brand_name}_links.json"
        with open(file_name, "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=4)

        print("-" * 30)
        print(f"✅ {brand_name} 저장 완료: {file_name}")
        print(f"✅ 수집된 유효 링크: {len(all_links)}개")
        print("-" * 30)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(crawl_chanel_links())
