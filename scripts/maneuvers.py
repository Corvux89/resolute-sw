import requests
import csv
import uuid

request = requests.get("https://sw5eapi.azurewebsites.net/api/maneuvers")

data = request.json()
output = [
    ["id", "name", "type", "source", "description", "pre-requisite"]
    ]

type_map = {
    "mental": 1,
    "physical": 2,
    "general": 3
}

for row in data:
    line = [
        uuid.uuid4(),
        row.get("name"),
        type_map.get(row.get("type").lower()),
        row.get("contentSourceEnum"),
        row.get("description"),
        row.get("prerequisite"),
    ]
    output.append(line)


with open("data.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerows(output)
