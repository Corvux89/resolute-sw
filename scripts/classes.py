import requests
import csv
import json

request = requests.get("https://sw5eapi.azurewebsites.net/api/class")

data = request.json()

class_map = {
    1: "Berserker",
    2: "Consular",
    3: "Engineer",
    4: "Fighter",
    5: "Guardian",
    6: "Monk",
    7: "Operative",
    8: "Scholar",
    9: "Scout",
    10: "Sentinel"
}

def level_table_markdown(json_data):
    
    headers = json.loads(json_data["levelChangeHeadersJson"])
    
    md = "| " + " | ".join(headers) + " |\n"
    md += "| " + " | ".join(["---"] * len(headers)) + " |\n"
    
    for i in range(1, 21):
        row = json_data["levelChanges"][str(i)]
        md += "| " + " | ".join(str(row.get(h, "")) for h in headers) + " |\n"

    return md

output = [
    [
        "id",
        "value",
        "summary",
        "primary_ability",
        "flavortext",
        "level_changes",
        "hit_die",
        "level_1_hp",
        "higher_hp",
        "armor_prof",
        "weapon_prof",
        "tool_prof",
        "saving_throws",
        "skill_choices",
        "starting_equipment",
        "features",
        "archetype_flavor",
        "image_url",
        "caster_type",
        "source"
    ]
]



for c in data:
    def get_value(key: str):
        val = c.get(key)

        if val == "None":
            return None
        return val

    class_id = next((k for k, v in class_map.items() if v == c.get('name')), None)
    class_value = next((v for k, v in class_map.items() if v == c.get('name')), None)

    if not class_id:
        print(f"Class: {c.get('name')} not found")
        continue

        
    if get_value('imageUrls'):
        image = get_value('imageUrls')[0]

    line = [
      class_id,
      class_value,
      get_value('summary'),
      get_value('primaryAbility'),
      get_value('flavorText'),
      level_table_markdown(c),
      get_value('hitDiceDieType')    ,
      get_value('hitPointsAtFirstLevel'),
      get_value('hitPointsAtHigherLevels'),
      ", ".join(c.get('armorProficiencies', [])),
      ", ".join(c.get('weaponProficiencies', [])),
      ", ".join(c.get('toolProficiencies', [])),      
      ", ".join(c.get('savingThrows', [])),
      get_value('skillChoices'),
      "\n".join(c.get('equipmentLines', [])),
      get_value('classFeatureText'),
      get_value('archetypeFlavorName'),
      image,
      get_value('casterTypeEnum') if get_value('casterTypeEnum') != 0 else None,
      get_value('contentSourceEnum')
    ]

    output.append(line)     

with open("data.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerows(output)