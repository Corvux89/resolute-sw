import requests
import csv
import uuid
import json

request = requests.get("https://sw5eapi.azurewebsites.net/api/background")

data = request.json()

output = [
    [
        "id",
        "name",
        "flavortext",
        "flavor_name",
        "flavor_description",
        "skills",
        "tools",
        "languages",
        "equipment",
        "suggested_characteristics",
        "feature_name",
        "feature_text",
        "feats",
        "personality",
        "ideal",
        "flaw",
        "bond",
        "source",
    ]
]


for obj in data:

    def make_feat_table(options, second_column_header):
        if not options:
            return None
        # Determine the first column header dynamically based on the length of options
        first_column_header = f"d{len(options)}"

        # Define the headers for the markdown table
        headers = [first_column_header, second_column_header]

        # Start the markdown table with headers
        md = "| " + " | ".join(headers) + " |\n"
        md += "| " + " | ".join(["---"] * len(headers)) + " |\n"

        # Add rows for each feat option
        for option in options:
            md += f"| {option['roll']} | [[{option['name']}]] |\n"

        return md

    def make_md_table(options, second_column_header):
        if not options:
            return None
        # Determine the first column header dynamically based on the length of options
        first_column_header = f"d{len(options)}"

        # Define the headers for the markdown table
        headers = [first_column_header, second_column_header]

        # Start the markdown table with headers
        md = "| " + " | ".join(headers) + " |\n"
        md += "| " + " | ".join(["---"] * len(headers)) + " |\n"

        # Add rows for each feat option
        for option in options:
            md += f"| {option['roll']} | {option['description']} |\n"

        return md

    def get_value(key: str, default: str = None):
        val = obj.get(key)

        if val == "None" or not val:
            return default
        return val

    line = [
        uuid.uuid4(),
        get_value("name"),
        get_value("flavorText"),
        get_value("flavorName"),
        get_value("flavorDescription"),
        get_value("skillProficiencies"),
        get_value("toolProficiencies"),
        get_value("languages"),
        get_value("equipment"),
        get_value("suggestedCharacteristics"),
        get_value("featureName"),
        get_value("featureText"),
        make_feat_table(get_value("featOptions"), "Feat"),
        make_md_table(get_value("personalityTraitOptions"), "Personality Trait"),
        make_md_table(get_value("idealOptions"), "Ideal"),
        make_md_table(get_value("flawOptions"), "Flaw"),
        make_md_table(get_value("bondOptions"), "Bond"),
        get_value("contentSourceEnum"),
    ]

    output.append(line)

with open("data.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerows(output)
