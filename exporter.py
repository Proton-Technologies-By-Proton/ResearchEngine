import csv
import os


def export_to_csv(data):
    os.makedirs("exports", exist_ok=True)

    path = "exports/output.csv"

    if not data:
        return path

    keys = data[0].keys()

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)

    return path