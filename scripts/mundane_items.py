import requests
import csv
import uuid

request = requests.get("https://sw5eapi.azurewebsites.net/api/equipment")

data = request.json()

output = [
    [
        "id",
        "source",
        "name",
        "description",
        "cost",
        "weight",
        "category",
        "dmg_number_of_die",
        "dmg_die_type",
        "dmg_type",
        "weapon_class",
        "armor_class",
        "properties",
        "ac",
        "stealth_dis"
    ]
]

for obj in data:
    image = None
    def get_value(key: str, default: str = None):
        val = obj.get(key)

        if val == "None":
            return default
        return val
    try:
        line = [
            uuid.uuid4(),
            get_value('contentSourceEnum'),
            get_value('name'),
            get_value('description'),
            get_value('cost'),
            get_value('weight'),
            get_value('equipmentCategoryEnum'),
            get_value('damageNumberOfDice'),
            get_value('damageDieType'),
            get_value('damageType') if get_value('damageType') != "Unknown" else None,
            get_value('weaponClassificationEnum') if get_value('weaponClassificationEnum') != 0 else None,
            get_value('armorClassificationEnum') if get_value('armorClassificationEnum') != 0 else None,
            ", ".join(get_value('properties')) if get_value('properties') else None,
            get_value('ac'),
            get_value('stealthDisadvantage')
        ]
    except Exception as e:
        print(obj.get('properties'))
        print(f"Issue with {obj.get('name')}: {e}")
        break

    output.append(line)

with open("data.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerows(output)