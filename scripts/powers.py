import requests
import csv

request = requests.get("https://sw5eapi.azurewebsites.net/api/power")

data = request.json()
output = [
    [
        "name",
        "pre-requisite",
        "type",
        "casttime",
        "range",
        "source",
        "description",
        "concentration",
        "alignment",
        "level",
        "duration",
    ]
]

for power in data:
    line = [
        power.get("name"),
        power.get("prerequisite"),
        (
            2
            if power.get("powerType") == "Tech"
            else 1 if power.get("powerType") == "Force" else None
        ),
        power.get("castingPeriodText"),
        power.get("range"),
        power.get("contentSourceEnum"),
        power.get("description"),
        power.get("concentration"),
        power.get("forceAlignmentEnum"),
        power.get("level"),
        power.get('duration', "Instantaneous")
    ]
    output.append(line)


with open("data.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerows(output)
