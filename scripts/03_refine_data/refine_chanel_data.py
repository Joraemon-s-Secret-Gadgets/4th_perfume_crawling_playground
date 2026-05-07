import json
import os

def refine_chanel_data(input_path, output_path):
    if not os.path.exists(input_path):
        print(f"File not found: {input_path}")
        return

    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    refined_data = []

    for item in data:
        # 1. Status check
        if item.get('status', '').lower() != 'success':
            continue

        # 2. N/A and essential field check
        first_impression = item.get('first_impression', '')
        scent_profile = item.get('scent_profile', '')
        if first_impression == 'N/A' or scent_profile == 'N/A' or not first_impression or not scent_profile:
            continue

        # 3. Canonical name from URL
        url = item.get('url', '')
        if 'perfume/' in url:
            name_part = url.split('perfume/')[-1]
            item['name'] = name_part.replace('-', ' ')
        else:
            item['name'] = item.get('name', 'Unknown')

        # 4. Check for essential lists
        notes = item.get('notes', {})
        has_notes = any(notes.get(key) for key in ['Top', 'Heart', 'Base'])
        accords = item.get('main_accords', [])
        
        if not has_notes or not accords:
            print(f"Skipping {item.get('name')} due to missing notes or accords.")
            continue

        # 5. Image check
        if item.get('image_url') == 'N/A':
            continue

        refined_data.append(item)

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(refined_data, f, ensure_ascii=False, indent=4)
    
    print(f"Successfully refined {len(refined_data)} Chanel items and saved to {output_path}")

if __name__ == "__main__":
    refine_chanel_data('raw/Chanel_final_data.json', 'refined/Chanel_final_data_refined.json')
