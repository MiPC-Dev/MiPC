import json

with open("example.json", "r", encoding="utf-8") as f:
    l = json.load(f)
with open("example.json", "w", encoding="utf-8") as f:
    json.dump(l, f, ensure_ascii=False, indent=4)