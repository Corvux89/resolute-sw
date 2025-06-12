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
        "sub_category",
        "properties",
        "ac",
        "stealth_dis"
    ]
]

subcategory_map = {
    3: {
        "SimpleBlaster": 1,
        "MartialBlaster": 2,
        "MartialVibroweapon": 3,
        "SimpleLightweapon": 4,
        "MartialLightweapon": 5,
        "ExoticBlaster": 6,
        "ExoticVibroweapon": 7,
        "ExoticLightweapon": 8
    },
    4: {
        "Light": 9,
        "Medium": 10,
        "Heavy": 11,
        "Shield": 12
    }
}

for obj in data:
    image = None
    def get_value(key: str, default: str = None): 
        val = obj.get(key)

        if val == "None":
            return default
        return val
    try:
        category = get_value('equipmentCategoryEnum')
        subcategory = None

        if sub_map := subcategory_map.get(category):
            if subcategory := sub_map.get(get_value('weaponClassification')):
                pass
            elif subcategory := sub_map.get(get_value('armorClassification')):
                pass


        line = [
            uuid.uuid4(),
            get_value('contentSourceEnum'),
            get_value('name'),
            get_value('description'),
            get_value('cost'),
            get_value('weight'),
            category,
            get_value('damageNumberOfDice'),
            get_value('damageDieType'),
            get_value('damageType') if get_value('damageType') != "Unknown" else None,
            subcategory,
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