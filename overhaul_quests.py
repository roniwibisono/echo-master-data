import json
import os
import glob

DATA_DIR = "/Users/rnddev/Documents/echo-master-data"

def load_json(filename):
    with open(os.path.join(DATA_DIR, filename), 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(data, filename):
    with open(os.path.join(DATA_DIR, filename), 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def main():
    print("Loading master data...")
    monsters_data = load_json("monster_master.json")
    monsters = monsters_data.get("monsters", [])
    world_map = load_json("world_map_v4.json")

    # 1. Map Monster codes to IDs and track spawns
    code_to_id = {}
    location_to_monsters = {}
    for m in monsters:
        m_id = m["monster_id"]
        m_code = m["code"]
        code_to_id[m_code] = m_id
        
        for loc in m.get("spawn_location", []):
            if loc not in location_to_monsters:
                location_to_monsters[loc] = []
            if m_id not in location_to_monsters[loc]:
                location_to_monsters[loc].append(m_id)

    # 2. Sync Map Spawns
    print("Fixing world_map_v4.json...")
    for region in world_map.get("nodes", []):
        r_id = region.get("id")
        r_name = region.get("name")
        
        # Combine monsters matching either region ID or Name
        target_monsters = []
        if r_id in location_to_monsters:
            target_monsters.extend(location_to_monsters[r_id])
        if r_name in location_to_monsters:
            target_monsters.extend(location_to_monsters[r_name])
            
        target_monsters = list(set(target_monsters)) # remove duplicates

        if target_monsters:
            existing_spawns = {s["monster_id"] for s in region.get("monster_spawns", [])}
            if r_id == "HIGHLAND_PLATEAU":
                print(f"Target: {target_monsters}, Existing: {existing_spawns}")
            missing_ids = [mid for mid in target_monsters if mid not in existing_spawns]
            
            if "monster_spawns" not in region:
                region["monster_spawns"] = []
                
            for mid in missing_ids:
                region["monster_spawns"].append({"monster_id": mid})
    
    save_json(world_map, "world_map_v4.json")

    # 3. Overhaul Quests
    print("Fixing quest files...")
    quest_files = glob.glob(os.path.join(DATA_DIR, "quest_*.json"))
    quest_files = [f for f in quest_files if not f.endswith("quest_reward_format_guide.json") and not f.endswith("quest_events.json") and not f.endswith("quest_list.json")]

    for q_file in quest_files:
        filename = os.path.basename(q_file)
        print(f"Processing {filename}...")
        try:
            with open(q_file, 'r', encoding='utf-8') as f:
                q_data = json.load(f)
        except Exception as e:
            print(f"Skipping {filename}, error: {e}")
            continue

        if "quests" not in q_data:
            continue
            
        for quest in q_data["quests"]:
            # Fix Objectives target (string -> int for kills)
            if "objectives" in quest:
                for obj in quest["objectives"]:
                    if obj.get("type") == "kill" and isinstance(obj.get("target"), str):
                        code = obj["target"]
                        if code in code_to_id:
                            obj["target_code"] = code
                            obj["target"] = code_to_id[code]
                            
            # Convert text description to interactive dialog nodes placeholder if needed
            # (Just structuring it for future UI)
            if "description" in quest and "dialog_nodes" not in quest:
                desc = quest["description"]
                quest["dialog_nodes"] = [
                    {"speaker": "quest_giver", "text": desc}
                ]
                
        save_json(q_data, filename)

    print("Overhaul complete.")

if __name__ == "__main__":
    main()
