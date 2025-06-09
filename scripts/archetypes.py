import requests
import csv
import json

request = requests.get("https://sw5eapi.azurewebsites.net/api/archetype")

data = request.json()

obj_map =  {'ballistic approach': {'id': '1', 'value': 'Ballistic Approach', 'parent': '1'}, 'cyclone approach': {'id': '2', 'value': 'Cyclone Approach', 'parent': '1'}, 'juggernaut approach': {'id': '3', 'value': 'Juggernaut Approach', 'parent': '1'}, 'marauder approach': {'id': '4', 'value': 'Marauder Approach', 'parent': '1'}, 'addicted approach': {'id': '5', 'value': 'Addicted Approach', 'parent': '1'}, 'armored approach': {'id': '6', 'value': 'Armored Approach', 'parent': '1'}, 'beastmaster approach': {'id': '7', 'value': 'Beastmaster Approach', 'parent': '1'}, 'bloodstorm approach': {'id': '8', 'value': 'Bloodstorm Approach', 'parent': '1'}, 'brawling approach': {'id': '9', 'value': 'Brawling Approach', 'parent': '1'}, 'champion approach': {'id': '10', 'value': 'Champion Approach', 'parent': '1'}, 'frenzied approach': {'id': '11', 'value': 'Frenzied Approach', 'parent': '1'}, 'industrial approach': {'id': '12', 'value': 'Industrial Approach', 'parent': '1'}, 'precision approach': {'id': '13', 'value': 'Precision Approach', 'parent': '1'}, 'warchief approach': {'id': '14', 'value': 'Warchief Approach', 'parent': '1'}, 'way of balance': {'id': '15', 'value': 'Way of Balance', 'parent': '2'}, 'way of lightning': {'id': '16', 'value': 'Way of Lightning', 'parent': '2'}, 'way of suggestion': {'id': '17', 'value': 'Way of Suggestion', 'parent': '2'}, 'way of the sage': {'id': '18', 'value': 'Way of the Sage', 'parent': '2'}, 'way of confluence': {'id': '19', 'value': 'Way of Confluence', 'parent': '2'}, 'way of endurance': {'id': '20', 'value': 'Way of Endurance', 'parent': '2'}, 'way of manipulation': {'id': '21', 'value': 'Way of Manipulation', 'parent': '2'}, 'way of negation': {'id': '22', 'value': 'Way of Negation', 'parent': '2'}, 'way of technology': {'id': '23', 'value': 'Way of Technology', 'parent': '2'}, 'way of telekinetics': {'id': '24', 'value': 'Way of Telekinetics', 'parent': '2'}, 'way of tutelage': {'id': '25', 'value': 'Way of Tutelage', 'parent': '2'}, 'way of the seer': {'id': '26', 'value': 'Way of the Seer', 'parent': '2'}, 'armormech engineering': {'id': '27', 'value': 'Armormech Engineering', 'parent': '3'}, 'armstech engineering': {'id': '28', 'value': 'Armstech Engineering', 'parent': '3'}, 'gadgeteer engineering': {'id': '29', 'value': 'Gadgeteer Engineering', 'parent': '3'}, 'unstable engineering': {'id': '30', 'value': 'Unstable Engineering', 'parent': '3'}, 'artificer engineering': {'id': '31', 'value': 'Artificer Engineering', 'parent': '3'}, 'astrotech engineering': {'id': '32', 'value': 'Astrotech Engineering', 'parent': '3'}, 'audiotech engineering': {'id': '33', 'value': 'Audiotech Engineering', 'parent': '3'}, 'biochem engineering': {'id': '34', 'value': 'Biochem Engineering', 'parent': '3'}, 'biotech engineering': {'id': '35', 'value': 'Biotech Engineering', 'parent': '3'}, 'construction engineering': {'id': '36', 'value': 'Construction Engineering', 'parent': '3'}, 'cybertech engineering': {'id': '37', 'value': 'Cybertech Engineering', 'parent': '3'}, 'assault specialist': {'id': '38', 'value': 'Assault Specialist', 'parent': '4'}, 'blademaster specialist': {'id': '39', 'value': 'Blademaster Specialist', 'parent': '4'}, 'shield specialist': {'id': '40', 'value': 'Shield Specialist', 'parent': '4'}, 'tactical specialist': {'id': '41', 'value': 'Tactical Specialist', 'parent': '4'}, 'adept specialist': {'id': '42', 'value': 'Adept Specialist', 'parent': '4'}, 'demolitions specialist': {'id': '43', 'value': 'Demolitions Specialist', 'parent': '4'}, 'enhancement specialist': {'id': '44', 'value': 'Enhancement Specialist', 'parent': '4'}, 'exhibition specialist': {'id': '45', 'value': 'Exhibition Specialist', 'parent': '4'}, 'fireteam specialist': {'id': '46', 'value': 'Fireteam Specialist', 'parent': '4'}, 'heavy weapons specialist': {'id': '47', 'value': 'Heavy Weapons Specialist', 'parent': '4'}, 'mounted specialist': {'id': '48', 'value': 'Mounted Specialist', 'parent': '4'}, 'praetorian specialist': {'id': '49', 'value': 'Praetorian Specialist', 'parent': '4'}, 'totem specialist': {'id': '50', 'value': 'Totem Specialist', 'parent': '4'}, 'makashi form': {'id': '51', 'value': 'Makashi Form', 'parent': '5'}, 'niman form': {'id': '52', 'value': 'Niman Form', 'parent': '5'}, 'shien/djem so form': {'id': '53', 'value': 'Shien/Djem So Form', 'parent': '5'}, 'soresu form': {'id': '54', 'value': 'Soresu Form', 'parent': '5'}, 'aqinos form': {'id': '55', 'value': 'Aqinos Form', 'parent': '5'}, 'ataru form': {'id': '56', 'value': 'Ataru Form', 'parent': '5'}, "jar'kai form": {'id': '57', 'value': "Jar'Kai Form", 'parent': '5'}, 'juyo/vaapad form': {'id': '58', 'value': 'Juyo/Vaapad Form', 'parent': '5'}, 'shii-cho form': {'id': '59', 'value': 'Shii-Cho Form', 'parent': '5'}, 'sokan form': {'id': '60', 'value': 'Sokan Form', 'parent': '5'}, 'trakata form': {'id': '61', 'value': 'Trakata Form', 'parent': '5'}, 'vonil/ishu form': {'id': '62', 'value': 'Vonil/Ishu Form', 'parent': '5'}, 'ysannanite form': {'id': '63', 'value': 'Ysannanite Form', 'parent': '5'}, 'crimson order': {'id': '64', 'value': 'Crimson Order', 'parent': '6'}, 'echani order': {'id': '65', 'value': 'Echani Order', 'parent': '6'}, 'matukai order': {'id': '66', 'value': 'Matukai Order', 'parent': '6'}, 'nightsister order': {'id': '67', 'value': 'Nightsister Order', 'parent': '6'}, 'aing-tii order': {'id': '68', 'value': 'Aing-Tii Order', 'parent': '6'}, 'jal shey order': {'id': '69', 'value': 'Jal Shey Order', 'parent': '6'}, 'kage order': {'id': '70', 'value': 'Kage Order', 'parent': '6'}, 'kro var order': {'id': '71', 'value': 'Kro Var Order', 'parent': '6'}, 'rakatan order': {'id': '72', 'value': 'Rakatan Order', 'parent': '6'}, 'teras kasi order': {'id': '73', 'value': 'Teras Kasi Order', 'parent': '6'}, 'trickster order': {'id': '74', 'value': 'Trickster Order', 'parent': '6'}, 'whills order': {'id': '75', 'value': 'Whills Order', 'parent': '6'}, 'acquisitions practice': {'id': '76', 'value': 'Acquisitions Practice', 'parent': '7'}, 'beguiler practice': {'id': '77', 'value': 'Beguiler Practice', 'parent': '7'}, 'lethality practice': {'id': '78', 'value': 'Lethality Practice', 'parent': '7'}, 'sharpshooter practice': {'id': '79', 'value': 'Sharpshooter Practice', 'parent': '7'}, 'bolstering practice': {'id': '80', 'value': 'Bolstering Practice', 'parent': '7'}, 'disabling practice': {'id': '81', 'value': 'Disabling Practice', 'parent': '7'}, 'gunslinger practice': {'id': '82', 'value': 'Gunslinger Practice', 'parent': '7'}, 'maverick practice': {'id': '83', 'value': 'Maverick Practice', 'parent': '7'}, 'performance practice': {'id': '84', 'value': 'Performance Practice', 'parent': '7'}, 'pugnacity practice': {'id': '85', 'value': 'Pugnacity Practice', 'parent': '7'}, 'ruffian practice': {'id': '86', 'value': 'Ruffian Practice', 'parent': '7'}, 'saboteur practice': {'id': '87', 'value': 'Saboteur Practice', 'parent': '7'}, 'sawbones practice': {'id': '88', 'value': 'Sawbones Practice', 'parent': '7'}, 'scrapper practice': {'id': '89', 'value': 'Scrapper Practice', 'parent': '7'}, 'shadow killer practice': {'id': '90', 'value': 'Shadow Killer Practice', 'parent': '7'}, 'gambler pursuit': {'id': '91', 'value': 'Gambler Pursuit', 'parent': '8'}, 'physician pursuit': {'id': '92', 'value': 'Physician Pursuit', 'parent': '8'}, 'politician pursuit': {'id': '93', 'value': 'Politician Pursuit', 'parent': '8'}, 'tactician pursuit': {'id': '94', 'value': 'Tactician Pursuit', 'parent': '8'}, 'archaeologist pursuit': {'id': '95', 'value': 'Archaeologist Pursuit', 'parent': '8'}, 'chef pursuit': {'id': '96', 'value': 'Chef Pursuit', 'parent': '8'}, 'detective pursuit': {'id': '97', 'value': 'Detective Pursuit', 'parent': '8'}, 'explorer pursuit': {'id': '98', 'value': 'Explorer Pursuit', 'parent': '8'}, 'geneticist pursuit': {'id': '99', 'value': 'Geneticist Pursuit', 'parent': '8'}, 'occultist pursuit': {'id': '100', 'value': 'Occultist Pursuit', 'parent': '8'}, 'slicer pursuit': {'id': '101', 'value': 'Slicer Pursuit', 'parent': '8'}, 'zoologist pursuit': {'id': '102', 'value': 'Zoologist Pursuit', 'parent': '8'}, 'bulwark technique': {'id': '103', 'value': 'Bulwark Technique', 'parent': '9'}, 'hunter technique': {'id': '104', 'value': 'Hunter Technique', 'parent': '9'}, 'slayer technique': {'id': '105', 'value': 'Slayer Technique', 'parent': '9'}, 'stalker technique': {'id': '106', 'value': 'Stalker Technique', 'parent': '9'}, 'artillerist technique': {'id': '107', 'value': 'Artillerist Technique', 'parent': '9'}, 'deadeye technique': {'id': '108', 'value': 'Deadeye Technique', 'parent': '9'}, 'illusionist technique': {'id': '109', 'value': 'Illusionist Technique', 'parent': '9'}, 'inquisitor technique': {'id': '110', 'value': 'Inquisitor Technique', 'parent': '9'}, 'mastermind technique': {'id': '111', 'value': 'Mastermind Technique', 'parent': '9'}, 'mechanist technique': {'id': '112', 'value': 'Mechanist Technique', 'parent': '9'}, 'predator technique': {'id': '113', 'value': 'Predator Technique', 'parent': '9'}, 'teleporation technique': {'id': '114', 'value': 'Teleporation Technique', 'parent': '9'}, 'triage technique': {'id': '115', 'value': 'Triage Technique', 'parent': '9'}, 'path of focus': {'id': '116', 'value': 'Path of Focus', 'parent': '10'}, 'path of shadows': {'id': '117', 'value': 'Path of Shadows', 'parent': '10'}, 'path of the corsair': {'id': '118', 'value': 'Path of the Corsair', 'parent': '10'}, 'path of the forceblade': {'id': '119', 'value': 'Path of the Forceblade', 'parent': '10'}, 'path of aggression': {'id': '120', 'value': 'Path of Aggression', 'parent': '10'}, 'path of communion': {'id': '121', 'value': 'Path of Communion', 'parent': '10'}, 'path of ethereality': {'id': '122', 'value': 'Path of Ethereality', 'parent': '10'}, 'path of iron': {'id': '123', 'value': 'Path of Iron', 'parent': '10'}, 'path of meditation': {'id': '124', 'value': 'Path of Meditation', 'parent': '10'}, 'path of synthesis': {'id': '125', 'value': 'Path of Synthesis', 'parent': '10'}, 'path of tenacity': {'id': '126', 'value': 'Path of Tenacity', 'parent': '10'}, 'path of witchcraft': {'id': '127', 'value': 'Path of Witchcraft', 'parent': '10'}, 'kyuzo order': {'id': '128', 'value': 'Kyuzo Order', 'parent': '6'}, 'teleportation technique': {'id': '129', 'value': 'Teleportation Technique', 'parent': '9'}}


def leveled_table_markdown(json_data):
    headers_json = json_data.get("leveledTableHeadersJson")
    if not headers_json:
        return None  # No table if headers are missing or None

    headers = json.loads(headers_json)
    md = "| " + " | ".join(headers) + " |\n"
    md += "| " + " | ".join(["---"] * len(headers)) + " |\n"

    levels = sorted(int(lvl) for lvl in json_data.get("leveledTable", {}).keys())
    for lvl in levels:
        row_list = json_data["leveledTable"].get(str(lvl), [])
        row_dict = {item["key"]: item["value"] for item in row_list if "key" in item and "value" in item}
        md += "| " + " | ".join(str(row_dict.get(h, "")) for h in headers) + " |\n"
    return md

output = [
    [
        "id",
        "parent",
        "value",
        "flavortext",
        "level_table",
        "image_url",
        "caster_type",
        "source"
    ]
]



for obj in data:
    image = None
    def get_value(key: str):
        val = obj.get(key)

        if val == "None":
            return None
        return val

    obj_record = obj_map.get(obj.get('name').lower())

    if not obj_record:
        print(f"{obj.get('name')} not found")
        continue

        
    if get_value('imageUrls'):
        image = get_value('imageUrls')[0]

    line = [
      obj_record.get('id'),
      obj_record.get('parent'),
      obj_record.get('value'),
      get_value('text'),
      leveled_table_markdown(obj),
      image,
      get_value('casterTypeEnum') if get_value('casterTypeEnum') != 0 else None,
      get_value('contentSourceEnum')
    ]

    output.append(line)     

with open("data.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerows(output)