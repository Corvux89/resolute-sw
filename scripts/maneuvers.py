import requests
import csv

request = requests.get('https://sw5eapi.azurewebsites.net/api/maneuvers')

data = request.json()
output = [
    ['name', 'type', 'source', 'description', 'pre-requisite']
    ]

for row in data:
    line = [
        row.get('name'),
        row.get('type'),
        row.get('contentSourceEnum'),
        row.get('description'),
        row.get('prerequisite')          
            ]
    output.append(line)


with open('data.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerows(output)
