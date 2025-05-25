import json
import csv
import sys
from pathlib import Path
from collections import defaultdict


def load_translations(csv_path: Path):
    trans_map = defaultdict(dict)
    with csv_path.open(encoding="utf-8") as csvf:
        reader = csv.DictReader(csvf)
        for row in reader:
            tr = row["translated_string"].strip()
            if not tr:
                continue
            file = row["file"]
            id_ = row["id"]
            trans_map[file][id_] = tr
    return trans_map


def apply_all(input_dir: Path, csv_path: Path, output_dir: Path):
    trans_map = load_translations(csv_path)

    for json_path in input_dir.rglob("*.json"):
        rel_file = str(json_path.relative_to(input_dir))
        if rel_file not in trans_map:
            # no translations for this file → copy as-is
            target = output_dir / rel_file
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(json_path.read_text(encoding="utf-8"), encoding="utf-8")
            continue

        data = json.loads(json_path.read_text(encoding="utf-8"))
        count = 0
        for label in data.get("labelDataArray", []):
            label_name = label.get("labelName", "")
            for idx, word in enumerate(label.get("wordDataArray", [])):
                row_id = f"{rel_file}::{label_name}:{idx}"
                if row_id in trans_map[rel_file]:
                    word["str"] = trans_map[rel_file][row_id]
                    count += 1

        target = output_dir / rel_file
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"{rel_file}: applied {count} translations")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(
            "Usage: python apply_all.py <input_json_dir> <translations_csv> <output_json_dir>"
        )
        sys.exit(1)
    input_dir = Path(sys.argv[1])
    csv_path = Path(sys.argv[2])
    output_dir = Path(sys.argv[3])
    apply_all(input_dir, csv_path, output_dir)
