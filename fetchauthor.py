import requests
import csv

base_url = "https://inspirehep.net/api/authors"
output_file = "table.csv"
total_pages = 7
page_size = 1000

data_rows = []

def format_name(name_data):
    if "preferred_name" in name_data:
        return name_data["preferred_name"]
    elif "value" in name_data:
        parts = name_data["value"].split(",", 1)
        if len(parts) == 2:
            surname = parts[0].strip()
            name = parts[1].strip()
            return f"{name} {surname}"
        else:
            return name_data["value"]
    else:
        return "Unknown Name"

count = 0

for page in range(1, total_pages + 1):
    params = {
        "sort": "bestmatch",
        "size": page_size,
        "page": page,
        "q": "positions.institution:CERN",
        "fields": "name"
    }

    response = requests.get(base_url, params=params)
    if response.status_code != 200:
        print(f"Failed to fetch page {page}: {response.status_code}")
        continue

    json_data = response.json()
    hits = json_data.get("hits", {}).get("hits", [])

    for author in hits:
        metadata = author.get("metadata", {})
        name_data = metadata.get("name", {})
        full_name = format_name(name_data)

        json_link = author.get("links", {}).get("json", "")
        if not json_link:
            continue  # skip if link is missing

        clean_link = json_link.replace("/api", "")

        data_rows.append([full_name, clean_link])
        count += 1

    print(f"Fetched page {page}: {len(hits)} authors")

# Write to CSV
with open(output_file, mode="w", newline='', encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["title", "content"])
    writer.writerows(data_rows)

print(f"\n✅ CSV file '{output_file}' created with {count} entries.")
