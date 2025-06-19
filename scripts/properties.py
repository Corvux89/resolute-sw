import requests
import csv
import json
import uuid

urls = [
    "https://sw5eapi.azurewebsites.net/api/ArmorProperty",
    "https://sw5eapi.azurewebsites.net/api/WeaponProperty",
] 

type = 0

output = [
    [
        "id",
        "name",
        "type",
        "text",
        "source",
    ]
]

for url in urls:
    type += 1
    request = requests.get(url)
    data = request.json()

    for obj in data:
        def get_value(key: str):
            val = obj.get(key)

            if val == "None":
                return None
            return val
         
        line = [
            uuid.uuid4(),
            get_value('name'),
            type,
            get_value('content'),
            get_value('contentSourceEnum'),
        ]

        output.append(line)

with open("data.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerows(output)