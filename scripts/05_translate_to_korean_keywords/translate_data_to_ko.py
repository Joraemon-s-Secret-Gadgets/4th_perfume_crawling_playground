import json
import os
import sys

# Import the translation maps
# Since it's in the root, we can append it to sys.path or just read it if it's simple.
# But it's easier to just import if we run from root.
sys.path.append(os.getcwd())
from perfume_translation_map import ACCORD_MAP, NOTE_MAP, PERFUME_NAME_MAP

def translate_item(item):
    new_item = item.copy()
    
    # 1. Translate Name
    name_en = item.get("name", "").lower()
    if name_en in PERFUME_NAME_MAP:
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
    files_to_process = [
        "Bvlgari_crawled_data_final.json",
        "Dior_crawled_data_final.json"
    ]
    
    for file in files_to_process:
        process_file(file)
