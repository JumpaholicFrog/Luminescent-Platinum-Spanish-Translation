import json
import csv
import sys
from pathlib import Path


def extract_all(input_dir: Path, output_csv: Path):
    rows = []
    for json_path in input_dir.rglob("*.json"):
        with json_path.open(encoding="utf-8") as f:
            data = json.load(f)
        rel_file = json_path.relative_to(input_dir)
        for label in data.get("labelDataArray", []):
            label_name = label.get("labelName", "")
            for idx, word in enumerate(label.get("wordDataArray", [])):
                text = word.get("str", "")
                # id includes file path to disambiguate
                row_id = f"{rel_file}::{label_name}:{idx}"
                rows.append(
                    {
                        "file": str(rel_file),
                        "id": row_id,
                        "original_string": text,
                        "translated_string": "",
                    }
                )

    # write CSV
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with output_csv.open("w", newline="", encoding="utf-8") as csvf:
        writer = csv.DictWriter(
            csvf, fieldnames=["file", "id", "original_string", "translated_string"]
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Extracted {len(rows)} strings into {output_csv}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python extract_all.py <input_json_dir> <output_csv_path>")
        sys.exit(1)
    input_dir = Path(sys.argv[1])
    output_csv = Path(sys.argv[2])
    extract_all(input_dir, output_csv)
