import asyncio
import random
import json
import re
import os
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

async def get_perfume_and_review(page, url, brand_name):
    """Extracted from scripts/crawl_fragrance_details.py"""
    data = {
        "brand": brand_name,
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
        response = await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(3)

        content = await page.content()
        if response.status >= 400 or "Worker Limit" in content or "1011" in content:
            print(f"⚠️ Limit detected - {url} skip")
            return None

        soup = BeautifulSoup(content, "html.parser")

        # Name
        name_tag = soup.find("h1")
        if name_tag:
            # Usually format is "Brand Name" or similar
            data["name"] = name_tag.text.strip().lower()

        img_tag = soup.select_one(".perfume-img-bg img")
        data["image_url"] = img_tag.get("src") if img_tag else "N/A"

        acc_h = soup.find(lambda t: t.name in ["h2", "h3"] and "Main Accords" in t.text)
        if acc_h:
            container = acc_h.find_next("div")
            for a in container.find_all("a", class_="group"):
                n, v = a.find("span", class_="w-24"), a.find("span", class_="tabular-nums")
                if n and v:
                    data["main_accords"].append(n.text.strip()) # Using only name for consistency with later refinement

        note_map = {"Top": "Top Notes", "Heart": "Heart Notes", "Base": "Base Notes"}
        for key, label in note_map.items():
            s = soup.find("span", string=lambda x: x and label in x)
            if s:
                lst = s.find_parent("div").find_next_sibling("div")
                if lst:
                    data["notes"][key] = [n.text.strip() for n in lst.select("span.flex-1")]

        s_h = soup.find(lambda t: "Best Season" in t.text)
        if s_h:
            s_d = s_h.find_next("div", class_="grid-cols-4")
            if s_d:
                # Get the season with highest percentage or list them?
                # Original refined data seems to just have a list.
                # Let's see the structure in Bvlgari_crawled_data_final.json
                # "usage_stats": { "Season": ["Spring", "Summer"], "Time": "Day" }
                seasons = ["Winter", "Spring", "Summer", "Fall"]
                percentages = [p.text.strip() for p in s_d.find_all("p", class_="font-semibold")]
                if len(percentages) == 4:
                    season_data = []
                    for s, p in zip(seasons, percentages):
                        p_val = int(p.replace('%', ''))
                        if p_val > 50: # Threshold or just take top?
                            season_data.append(s)
                    if not season_data: # If none above 50, take top 2
                        sorted_seasons = sorted(zip(seasons, [int(p.replace('%', '')) for p in percentages]), key=lambda x: x[1], reverse=True)
                        season_data = [sorted_seasons[0][0], sorted_seasons[1][0]]
                    data["usage_stats"]["Season"] = season_data

        t_h = soup.find(lambda t: "Day & Night" in t.text)
        if t_h:
            t_d = t_h.find_next("div", class_="grid-cols-2")
            if t_d:
                times = ["Day", "Night"]
                percentages = [p.text.strip() for p in t_d.find_all("p", class_="font-semibold")]
                if len(percentages) == 2:
                    p_day = int(percentages[0].replace('%', ''))
                    p_night = int(percentages[1].replace('%', ''))
                    data["usage_stats"]["Time"] = "Day" if p_day >= p_night else "Night"

        # Review
        review_url = url.replace("/perfume/", "/reviews/")
        r_response = await page.goto(review_url, wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(5)

        r_content = await page.content()
        if r_response.status >= 400 or "Worker Limit" in r_content:
            data["status"] = "Review Skipped (Limit)"
            return data

        r_soup = BeautifulSoup(r_content, "html.parser")

        fi_h = r_soup.find(lambda t: t.name in ["h2", "h3"] and re.search(r"First Impression", t.get_text(), re.I))
        if fi_h:
            paras = []
            curr = fi_h.find_next_sibling()
            while curr and curr.name == "p":
                paras.append(curr.get_text(strip=True).replace("''", "'"))
                curr = curr.find_next_sibling()
            data["first_impression"] = "\n".join(paras)

        sp_h = r_soup.find(lambda t: t.name in ["h2", "h3"] and re.search(r"Scent Profile", t.get_text(), re.I))
        if sp_h:
            paras = []
            curr = sp_h.find_next_sibling()
            while curr and curr.name == "p":
                paras.append(curr.get_text(strip=True).replace("''", "'"))
                curr = curr.find_next_sibling()
            data["scent_profile"] = "\n".join(paras)

        return data

    except Exception as e:
        print(f"❌ Error ({url}): {e}")
        return None

async def crawl_chanel_details():
    brand_name = "Chanel"
    links_file = "raw/Chanel_links.json"
    output_file = "raw/Chanel_final_data.json"
    partial_file = "raw/Chanel_data_partial.json"

    if not os.path.exists(links_file):
        print(f"File not found: {links_file}")
        return

    with open(links_file, "r", encoding="utf-8") as f:
        urls = json.load(f).get("links", [])

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        )
        page = await context.new_page()

        results = []
        # Start from where we left off if partial exists?
        # For now, start fresh or just process all.
        
        print(f"\n🌟 Starting {brand_name} ({len(urls)} items)...")

        for i, url in enumerate(urls):
            print(f"🔄 [{brand_name}] {i+1}/{len(urls)}: {url}")
            res = await get_perfume_and_review(page, url, brand_name)

            if res:
                # Fix name to remove brand if it's there
                if "name" in res:
                    res["name"] = res["name"].replace("chanel", "").strip()
                results.append(res)

            if (i + 1) % 10 == 0:
                cooldown = random.uniform(10, 15)
                print(f"😴 Cooldown ({cooldown:.2f}s)...")
                await asyncio.sleep(cooldown)
                
                # Intermediate save
                with open(partial_file, "w", encoding="utf-8") as f:
                    json.dump(results, f, ensure_ascii=False, indent=4)
            else:
                await asyncio.sleep(random.uniform(2, 4))

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=4)

        await browser.close()
        print(f"\n✅ {brand_name} Complete!")

if __name__ == "__main__":
    asyncio.run(crawl_chanel_details())
