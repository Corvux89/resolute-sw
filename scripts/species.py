import requests
import csv

request = requests.get("https://sw5eapi.azurewebsites.net/api/species")

data = request.json()

species_map = {
    1:"Bith",
    2:"Bothan",
    3:"Cathar",
    4:"Cerean",
    5:"Chiss",
    6:"Devaronian",
    7:"Droid, Class I",
    8:"Droid, Class II",
    9:"Droid, Class III",
    10:"Droid, Class IV",
    11:"Droid, Class V",
    12:"Duros",
    13:"Ewok",
    14:"Gamorrean",
    15:"Gungan",
    16:"Human",
    17:"Ithorian",
    18:"Jawa",
    19:"Kel Dor",
    20:"Mon Calamari",
    21:"Nautolan",
    22:"Rodian",
    23:"Sith Pureblood",
    24:"Togruta",
    25:"Trandoshan",
    26:"Tusken",
    27:"Twi'lek",
    28:"Weequay",
    29:"Wookiee",
    30:"Zabrak",
    31:"Abyssin",
    32:"Advozse",
    33:"Aing-Tii",
    34:"Aleena",
    35:"Anomid",
    36:"Anx",
    37:"Anzellan",
    38:"Aqualish",
    39:"Arcona",
    40:"Ardennian",
    41:"Arkanian",
    42:"Balosar",
    43:"Barabel",
    44:"Baragwin",
    45:"Besalisk",
    46:"Caamasi",
    47:"Chadra-Fan",
    48:"Chagrian",
    49:"Chevin",
    50:"Chironian",
    51:"Clawdite",
    52:"Codru-Ji",
    53:"Colicoid",
    54:"Culisetto",
    55:"Dashade",
    56:"Defel",
    57:"Diathim",
    58:"Dowutin, Young",
    59:"Draethos",
    60:"Dug",
    61:"Echani",
    62:"Esh-Kha",
    63:"Falleen",
    64:"Felucian",
    65:"Flesh Raider",
    66:"Gand",
    67:"Gank",
    68:"Geonosian",
    69:"Givin",
    70:"Gormak",
    71:"Gotal",
    72:"Gran",
    73:"Half-human",
    74:"Harch",
    75:"Herglic",
    76:"Ho'din",
    77:"Houk",
    78:"Hutt, Adolescent",
    79:"Iktotchi",
    80:"Kage",
    81:"Kaleesh",
    82:"Kalleran",
    83:"Kaminoan",
    84:"Karkarodon",
    85:"Kiffar",
    86:"Killik",
    87:"Klatooinian",
    88:"Kubaz",
    89:"Kushiban",
    90:"Kyuzo",
    91:"Lannik",
    92:"Lasat",
    93:"Lurmen",
    94:"Massassi",
    95:"Mikkian",
    96:"Miraluka",
    97:"Mirialan",
    98:"Mustafarian",
    99:"Muun",
    100:"Neimoidian",
    101:"Nikto",
    102:"Noghri",
    103:"Nothoiin",
    104:"Ortolan",
    105:"Pa'lowick",
    106:"Pantoran",
    107:"Patrolian",
    108:"Pau'an",
    109:"Pyke",
    110:"Quarren",
    111:"Quermian",
    112:"Rakata",
    113:"Rattataki",
    114:"Rishii",
    115:"Ryn",
    116:"Selkath",
    117:"Selonian",
    118:"Shistavanen",
    119:"Squib",
    120:"Ssi-Ruu",
    121:"Sullustan",
    122:"Talz",
    123:"Tarasin",
    124:"Taung",
    125:"Theelin",
    126:"Thisspiasian",
    127:"Tiss'shar",
    128:"Tognath",
    129:"Togorian",
    130:"Toydarian",
    131:"Ugnaught",
    132:"Ugor",
    133:"Umbaran",
    134:"Verpine",
    135:"Voss",
    136:"Vurk",
    137:"Xexto",
    138:"Yevetha",
    139:"Zeltron",
    140:"Zilkin",
    141:"Zygerrian",
    142:"Custom Lineage*"
}

output = [
    [
        "id",
        "value",
        "skin_options",
        "hair_options",
        "eye_options",
        "distinctions",
        "height_average",
        "height_mod",
        "weight_average",
        "weight_mod",
        "homeworld",
        "flavortext",
        "language",
        "image_url",
        "size",
        "source",
        "traits"
    ]
]



for species in data:
    abilities = []
    trait_text = []
    image = None

    def get_value(key: str):
        val = species.get(key)

        if val == "None":
            return None
        return val

    species_id = next((k for k, v in species_map.items() if v == species.get('name')), None)
    species_value = next((v for k, v in species_map.items() if v == species.get('name')), None)

    if not species_id:
        print(f"Secies: {species.get('name')} not found")
        continue

    for trait in species.get('traits', []):
        trait_text.append(f'''**{trait.get('name')}.** {trait.get('description')}''')
        
    if get_value('imageUrls'):
        image = get_value('imageUrls')[0]

    line = [
        species_id,
        species.get('name'),
        species.get('skinColorOptions'),
        species.get('hairColorOptions'),
        species.get('eyeColorOptions'),
        species.get('distinctions'),
        species.get('heightAverage'),
        species.get('heightRollMod'),
        species.get('weightAverage'),
        species.get('weightRollMod'),
        species.get('homeworld'),
        species.get('flavorText'),
        species.get('language'),
        image,
        species.get('size'),
        species.get('contentSourceEnum'),
        "\n\n".join(trait_text)
    ]

    output.append(line)     

with open("data.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerows(output)