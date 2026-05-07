import json
import os

def refine_data(file_path, output_path):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            print(f"Error decoding JSON in {file_path}")
            return

    refined_data = []

    for item in data:
        # 1. Filter by status 'success' (case-insensitive)
        status = item.get('status', '')
        if status.lower() != 'success':
            continue

        # 2. Exclude if first_impression or scent_profile is 'N/A'
        first_impression = item.get('first_impression', '')
        scent_profile = item.get('scent_profile', '')
        if first_impression == 'N/A' or scent_profile == 'N/A':
            continue

        # 3. Create 'name' field from URL
        # Example: https://fraganty.ai/perfume/omnia-crystalline -> omnia crystalline
        url = item.get('url', '')
        if 'perfume/' in url:
            name_part = url.split('perfume/')[-1]
            item['name'] = name_part.replace('-', ' ')
        else:
            item['name'] = 'Unknown'

        # 4. Simplify main_accords: extract 'accord' only
        if 'main_accords' in item and isinstance(item['main_accords'], list):
            item['main_accords'] = [acc['accord'] for acc in item['main_accords'] if 'accord' in acc]

        # 5. Process usage_stats
        usage_stats = item.get('usage_stats', {})
        
        # Season: list of season names with percentage >= 70%
        seasons = usage_stats.get('Season', {})
        if seasons:
            refined_seasons = []
            for s_name, s_pct_str in seasons.items():
                try:
                    pct = int(s_pct_str.replace('%', ''))
                    if pct >= 70:
                        refined_seasons.append(s_name)
                except (ValueError, AttributeError):
                    continue
            item['usage_stats']['Season'] = refined_seasons
        
        # Time: keep only the label (Day/Night) with higher percentage
        times = usage_stats.get('Time', {})
        if times:
            max_time = None
            max_val = -1
            for t_name, t_pct_str in times.items():
                try:
                    pct = int(t_pct_str.replace('%', ''))
                    if pct > max_val:
                        max_val = pct
                        max_time = t_name
                except (ValueError, AttributeError):
                    continue
            item['usage_stats']['Time'] = max_time

        refined_data.append(item)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(refined_data, f, ensure_ascii=False, indent=4)
    
    print(f"Successfully refined {len(refined_data)} items and saved to {output_path}")

if __name__ == "__main__":
    files_to_process = [
        ("Bvlgari_final_data.json", "Bvlgari_final_data_refined.json"),
        ("Dior_final_data.json", "Dior_final_data_refined.json")
    ]

    for input_file, output_file in files_to_process:
        refine_data(input_file, output_file)
