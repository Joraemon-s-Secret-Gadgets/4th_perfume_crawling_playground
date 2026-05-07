import json
import os

def get_country(brand):
    if brand == "Bvlgari":
        return "이탈리아"
    if brand in ["Chanel", "Dior"]:
        return "프랑스"
    return "N/A"

def convert_brand(brand_name, final_en_path, final_ko_path):
    print(f"Processing {brand_name}...")
    with open(final_en_path, 'r', encoding='utf-8') as f:
        data_en = json.load(f)
    with open(final_ko_path, 'r', encoding='utf-8') as f:
        data_ko = json.load(f)
    
    # Create lookup for English names and AI analysis
    en_lookup = {}
    for item in data_en:
        en_lookup[item['url']] = {
            'name': item.get('name', ''),
            'ai_analysis': item.get('ai_analysis', {})
        }
    
    converted = []
    for item in data_ko:
        url = item.get('url', '')
        en_data = en_lookup.get(url, {})
        
        # English name exactly as in English final file
        english_name = en_data.get('name', '')
        
        # Price: use retail as is
        price_info = item.get('price_info', {})
        retail = price_info.get('retail', '')
        if isinstance(retail, list) and retail:
            regular_price = str(retail[0])
        else:
            regular_price = str(retail) if retail else ""
            
        # Key Ingredients: all notes (Korean) flattened
        all_notes = []
        notes = item.get('notes', {})
        for category in ['Top', 'Heart', 'Base']:
            all_notes.extend(notes.get(category, []))
        
        # Keywords from accords (Korean)
        accords = item.get('main_accords', [])
        
        # AI Keywords
        ko_keywords = []
        en_keywords = []
        
        # From Korean data (moods/occasions)
        ko_analysis = item.get('ai_analysis', {})
        if ko_analysis:
            ko_keywords.extend(ko_analysis.get('moods', []))
            ko_keywords.extend(ko_analysis.get('occasions', []))
            
        # From English data (moods/occasions)
        en_analysis = en_data.get('ai_analysis', {})
        if en_analysis:
            # The English moods/occasions in the 'final' file are lists of dicts with 'en' and 'ko' keys
            en_moods = [m['en'] for m in en_analysis.get('moods', []) if isinstance(m, dict) and 'en' in m]
            en_occasions = [o['en'] for o in en_analysis.get('occasions', []) if isinstance(o, dict) and 'en' in o]
            en_keywords.extend(en_moods)
            en_keywords.extend(en_occasions)
        
        # Final formatting
        entry = {
            "country": get_country(brand_name),
            "korean_name": item.get('name', ''),
            "english_name": english_name,
            "product_type": "향수",
            "product_url": url,
            "regular_price": regular_price,
            "image_url": item.get('image_url', ''),
            "ingredients": "",
            "key_ingredients": list(dict.fromkeys(all_notes)),
            "keywords": accords,
            "ko_keywords": list(dict.fromkeys(ko_keywords)),
            "en_keywords": list(dict.fromkeys(en_keywords))
        }
        converted.append(entry)
    
    output_path = f"refined/{brand_name}_final_formatted_v2.json"
    if not os.path.exists('refined'):
        os.makedirs('refined')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(converted, f, ensure_ascii=False, indent=4)
    print(f"Saved {len(converted)} items to {output_path}")

if __name__ == "__main__":
    brands = [
        ("Bvlgari", "Bvlgari_crawled_data_final.json", "Bvlgari_crawled_data_final_ko.json"),
        ("Chanel", "Chanel_crawled_data_final.json", "Chanel_crawled_data_final_ko.json"),
        ("Dior", "Dior_crawled_data_final.json", "Dior_crawled_data_final_ko.json")
    ]
    
    for brand, en, ko in brands:
        if os.path.exists(en) and os.path.exists(ko):
            convert_brand(brand, en, ko)
        else:
            print(f"Files missing for {brand}: {en} or {ko}")
