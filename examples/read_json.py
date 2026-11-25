import json

with open("new_file.json", "r", encoding="utf-8") as file:
    data = json.load(file)

print(data)