import requests
import csv
import uuid

request = requests.get("https://sw5eapi.azurewebsites.net/api/feat")

data = request.json()

output = [
    [
        "id",
        "name",
        "prerequisite",
        "text",
        "source",
        "attributes"
    ]
]

for obj in data:
    def get_value(key: str, default: str = None): 
        val = obj.get(key)

        if val == "None" or not val:
            return default
        return val

    atrributes = get_value("attributesIncreased", [])

    attr_string = ", ".join(atrributes)


            
    
    line = [
        uuid.uuid4(),
        get_value("name"),
        get_value("prerequisite"),
        get_value("text"),
        get_value("contentSourceEnum"),
        f"{{{attr_string}}}"
    ]

    output.append(line)

with open("data.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file, quotechar="$")
    writer.writerows(output)