import pandas as pd
import json
import os
from typing import Any


def update_json_from_csv(csv_path, profiles_dir):
    df = pd.read_csv(csv_path)
    df.columns = [str(col).strip() for col in df.columns]

    for index, row in df.iterrows():
        artist_id = str(row['Artist ID']).strip().zfill(2)
        file_path = os.path.join(profiles_dir, f"artist_{artist_id}.json")

        # --- THE BLUEPRINT STRATEGY ---
        # If the file exists, we load it. If not, we start with this full template.
        if os.path.exists(file_path):
            with open(file_path, 'r') as json_file:
                profile_data = json.load(json_file)
        else:
            print(f"✨ Creating full blueprint for new artist: {artist_id}")
            profile_data = {
                "id": artist_id,
                "name": "",
                "email": "",
                "primary_genre": "",
                "target_market_genre": "",
                "search_keyword": [],
                "sync_checklist": {},
                "focus_area_message": "Add your weekly focus message here.",
                "focus_area_link": "",
                "thresholds": {"growth": 0.25}, # Default growth goal
                "data_sources": {
                    "spotify_id": "PASTE_ID_HERE",
                    "manual_csv": f"artist_{artist_id}.csv" # Auto-suggests a filename
                }
            }

        # --- UPDATE DATA FROM CSV ---
        profile_data['name'] = row['Artist Name']
        profile_data['email'] = row['Email']
        profile_data['primary_genre'] = row['Primary Genre']
        profile_data['target_market_genre'] = row['Target Market']
        raw_input = str(row['Search Keyword'])
        artist_keywords = [k.strip() for k in raw_input.split(',') if k.strip()]
        profile_data['search_keyword'] = artist_keywords[:5]

        # Sync Checklist logic
        profile_data['sync_checklist'] = {
            "one_stop_ownership": int(str(row['One Stop'])[0]),
            "writer_splits_captured": int(str(row['Splits'])[0]),
            "isrc_iswc_embedded": int(str(row['Metadata'])[0]),
            "alt_versions_ready": int(str(row['Alts'])[0]),
            "searchable_tags": int(str(row['Tags'])[0]),
            "contact_sla_included": int(str(row['SLA'])[0])
        }

        # Save the structured JSON
        with open(file_path, 'w', encoding='utf-8') as json_file:
            json.dump(profile_data, json_file, indent=2)  # <--- Now they match!

    print("✅ All profiles updated with full structure blueprints.")
if __name__ == "__main__":
    update_json_from_csv('latest_responses.csv', 'profiles/')
