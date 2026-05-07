import json
import os
import sys

# Import mapping
sys.path.append(os.getcwd())
from perfume_translation_map import ACCORD_MAP, NOTE_MAP, PERFUME_NAME_MAP

# Additional Chanel mappings for perfume names
CHANEL_NAME_MAP = {
    "coco mademoiselle": "코코 마드모아젤",
    "bleu de chanel eau de parfum": "블루 드 샤넬 오 드 퍼퓸",
    "bleu de chanel": "블루 드 샤넬",
    "chance eau tendre": "샹스 오 땅드르",
    "chance eau fraiche": "샹스 오 후레쉬",
    "allure homme sport": "알뤼르 옴므 스포츠",
    "chanel no 5 parfum": "샤넬 N°5 파퓸",
    "coco eau de parfum": "코코 오 드 퍼퓸",
    "chance eau de toilette": "샹스 오 드 뚜왈렛",
    "allure homme sport eau extreme": "알뤼르 옴므 스포츠 오 익스트림",
    "egoiste platinum": "에고이스트 플래티넘",
    "coco noir": "코코 느와르",
    "chanel no 5 eau de parfum": "샤넬 N°5 오 드 퍼퓸",
    "bleu de chanel parfum": "블루 드 샤넬 퍼퓸",
    "gabrielle": "가브리엘",
    "egoiste": "에고이스트",
    "allure sensuelle": "알뤼르 썽슈엘",
    "allure homme": "알뤼르 옴므",
    "chanel no 5 l eau": "샤넬 N°5 로",
    "chanel no 19 eau de parfum": "샤넬 N°19 오 드 퍼퓸",
    "chance eau de parfum": "샹스 오 드 퍼퓸",
    "coco mademoiselle intense": "코코 마드모아젤 인텐스",
    "chanel n 5 eau premiere": "샤넬 N°5 오 프르미에르",
    "coco mademoiselle eau de toilette": "코코 마드모아젤 오 드 뚜왈렛",
    "allure": "알뤼르",
    "antaeus": "안테우스",
    "chanel no 5 eau de toilette": "샤넬 N°5 오 드 뚜왈렛",
    "chanel no 19 poudre": "샤넬 N°19 뿌드르",
    "chanel n 19": "샤넬 N°19",
    "cristalle eau verte": "크리스탈 오 verte",
    "les exclusifs de chanel coromandel": "레 엑스클루시브 드 샤넬 코로망델",
    "chanel no 5 eau premiere 2015": "샤넬 N°5 오 프르미에르 (2015)",
    "allure homme edition blanche eau de parfum": "알뤼르 옴므 에디션 블랑쉬 오 드 퍼퓸",
    "chance eau vive": "샹스 오 비브",
    "cristalle eau de toilette": "크리스탈 오 드 뚜왈렛",
    "chance eau tendre eau de parfum": "샹스 오 땅드르 오 드 퍼퓸",
    "gabrielle essence": "가브리엘 에센스",
    "coromandel eau de parfum": "코로망델 오 드 퍼퓸",
    "coco mademoiselle parfum": "코코 마드모아젤 파퓸",
    "les exclusifs de chanel sycomore": "레 엑스클루시브 드 샤넬 시코모르",
    "allure homme sport cologne": "알뤼르 옴므 스포츠 코롱",
    "les exclusifs de chanel beige": "레 엑스클루시브 드 샤넬 베쥬",
    "le lion eau de parfum": "르 리옹 오 드 퍼퓸",
    "pour monsieur": "뿌르 므슈",
    "coco eau de toilette": "코코 오 드 뚜왈렛",
    "cristalle eau de parfum": "크리스탈 오 드 퍼퓸",
    "sycomore eau de parfum": "시코모르 오 드 퍼퓸",
    "bleu de chanel l exclusif": "블루 드 샤넬 렉스클루시브",
    "1957 eau de parfum": "1957 오 드 퍼퓸",
    "gard nia": "가드니아",
    "bois des iles": "보아 데 질",
    "les exclusifs de chanel 31 rue cambon": "레 엑스클루시브 드 샤넬 31 뤼 캉봉",
    "chance eau splendide": "샹스 오 스플랑디드",
    "paris venise": "파리-베니스",
    "chance eau fraiche eau de parfum": "샹스 오 후레쉬 오 드 퍼퓸",
    "beige eau de parfum": "베쥬 오 드 퍼퓸",
    "chanel no 19 parfum": "샤넬 N°19 파퓸",
    "boy eau de parfum": "보이 오 드 퍼퓸",
    "com te": "코메트",
    "les exclusifs de chanel jersey": "레 엑스클루시브 드 샤넬 져지",
    "allure homme sport superleggera": "알뤼르 옴므 스포츠 슈퍼레제라",
    "chanel n 22": "샤넬 N°22",
    "paris deauville": "파리-도빌",
    "les exclusifs de chanel misia": "레 엑스클루시브 드 샤넬 미시아",
    "paris dimbourg": "파리-에든버러",
    "coco mademoiselle l eau priv e": "코코 마드모아젤 로 프리베",
    "les exclusifs de chanel no 22": "레 엑스클루시브 드 샤넬 N°22",
    "les exclusifs de chanel cuir de russie": "레 엑스클루시브 드 샤넬 뀌르 드 뤼시",
    "allure sensuelle eau de toilette": "알뤼르 썽슈엘 오 드 뚜왈렛",
    "jersey eau de parfum": "져지 오 드 퍼퓸",
    "les exclusifs de chanel 28 la pausa": "레 엑스클루시브 드 샤넬 28 라 파우자",
    "allure eau de toilette": "알뤼르 오 드 뚜왈렛",
    "allure parfum": "알뤼르 파퓸",
    "les exclusifs de chanel no 18": "레 엑스클루시브 드 샤넬 N°18",
    "pour monsieur eau de parfum": "뿌르 므슈 오 드 퍼퓸",
    "les exclusifs de chanel bel respiro": "레 엑스클루시브 드 샤넬 벨 레스피로",
    "gabrielle parfum": "가브리엘 파퓸",
    "la pausa eau de parfum": "라 파우자 오 드 퍼퓸",
    "allure homme sport eau de toilette": "알뤼르 옴므 스포츠 오 드 뚜왈렛",
    "bel respiro eau de parfum": "벨 레스피로 오 드 퍼퓸",
    "cuir de russie eau de parfum": "뀌르 드 뤼시 오 드 퍼퓸",
    "coco mademoiselle l extrait": "코코 마드모아젤 렉스트레",
    "cuir de russie": "뀌르 드 뤼시",
    "les exclusifs de chanel sycomore parfum": "레 엑스클루시브 드 샤넬 시코모르 파퓸",
    "cristalle": "크리스탈",
    "egoiste platinum eau de toilette": "에고이스트 플래티넘 오 드 뚜왈렛",
    "le lion de chanel parfum": "르 리옹 드 샤넬 파퓸",
    "les exclusifs de chanel 1932": "레 엑스클루시브 드 샤넬 1932",
    "misia eau de parfum": "미시아 오 드 퍼퓸",
    "gard nia eau de parfum": "가드니아 오 드 퍼퓸",
    "chanel no 19 eau de toilette": "샤넬 N°19 오 드 뚜왈렛",
    "1932 eau de parfum": "1932 오 드 퍼퓸",
    "les exclusifs de chanel coromandel parfum": "레 엑스클루시브 드 샤넬 코로망델 파퓸",
    "paris biarritz": "파리-비아리츠",
    "paris riviera": "파리-리비에라",
    "paris paris": "파리-파리",
    "chance parfum": "샹스 파퓸",
    "n 18 eau de parfum": "N°18 오 드 퍼퓸",
    "bois des iles eau de parfum": "보아 데 질 오 드 퍼퓸",
    "les exclusifs de chanel gardenia parfum": "레 엑스클루시브 드 샤넬 가드니아 파퓸",
    "gard nia extrait de parfum": "가드니아 엑스트레 드 파퓸",
    "chance hair mist": "샹스 헤어 미스트",
    "chanel no 5 eau de parfum 2024 limited edition": "샤넬 N°5 오 드 퍼퓸 (2024 한정판)",
    "coco mademoiselle fragrance primer": "코코 마드모아젤 프래그런스 프라이머",
    "chanel no 46": "샤넬 N°46",
    "allure eau fra chissante pour l t": "알뤼르 오 후레쉬 뿌르 레테",
    "coco noir hair mist": "코코 느와르 헤어 미스트",
    "chanel no 5 parfum baccarat grand extrait": "샤넬 N°5 파퓸 바카라 그랑 엑스트레",
    "le 1940 bleu de chanel": "르 1940 블루 드 샤넬",
    "gabrielle fragrance primer": "가브리엘 프래그런스 프라이머",
    "le 1940 beige de chanel": "르 1940 베쥬 드 샤넬",
    "le 1940 rouge de chanel": "르 1940 루쥬 드 샤넬",
    "chanel n 5 voile parfum": "샤넬 N°5 브왈 파퓸",
    "coco voile parfum": "코코 브왈 파퓸",
    "chanel n 19 voile parfum": "샤넬 N°19 브왈 파퓸",
    "antaeus sport cologne": "안테우스 스포츠 코롱"
}

def translate_item(item):
    new_item = item.copy()
    
    # 1. Translate Name
    name_en = item.get("name", "").lower()
    if name_en in CHANEL_NAME_MAP:
        new_item["name"] = CHANEL_NAME_MAP[name_en]
    elif name_en in PERFUME_NAME_MAP:
        new_item["name"] = PERFUME_NAME_MAP[name_en]
    
    # 2. Translate Main Accords
    if "main_accords" in item:
        new_item["main_accords"] = [ACCORD_MAP.get(accord, accord) for accord in item["main_accords"]]
    
    # 3. Translate Notes
    if "notes" in item:
        new_notes = {}
        for category, note_list in item["notes"].items():
            new_notes[category] = [NOTE_MAP.get(note, note) for note in note_list]
        new_item["notes"] = new_notes
        
    # 4. Simplify AI Analysis
    if "ai_analysis" in item and item["ai_analysis"]:
        ai = item["ai_analysis"]
        new_ai = {}
        
        if "moods" in ai:
            new_ai["moods"] = [m.get("ko", m.get("en")) if isinstance(m, dict) else m for m in ai["moods"]]
        
        if "occasions" in ai:
            new_ai["occasions"] = [o.get("ko", o.get("en")) if isinstance(o, dict) else o for o in ai["occasions"]]
            
        if "gender_profile" in ai:
            gp = ai["gender_profile"]
            new_ai["gender_profile"] = gp.get("ko", gp.get("en")) if isinstance(gp, dict) else gp
            
        if "strength_score" in ai:
            new_ai["strength_score"] = ai["strength_score"]
            
        if "reasoning" in ai:
            new_ai["reasoning"] = ai["reasoning"]
            
        new_item["ai_analysis"] = new_ai
        
    return new_item

def process_file(file_path):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return
    
    print(f"Processing {file_path}...")
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    translated_data = [translate_item(item) for item in data]
    
    output_path = file_path.replace(".json", "_ko.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(translated_data, f, ensure_ascii=False, indent=4)
    
    print(f"Saved to {output_path}")

if __name__ == "__main__":
    process_file("Chanel_crawled_data_final.json")
