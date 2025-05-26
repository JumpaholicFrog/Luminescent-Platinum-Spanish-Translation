#!/usr/bin/env python3
import json
import sys
from pathlib import Path

def extract_translations(flat_path: Path) -> dict:
    """
    Load the flat JSON of translations, which maps keys like
    "DLP_adventure_note_001_00_0" → "Translated text"
    """
    if not flat_path.is_file():
        print(f"[ERROR] Flat JSON not found: {flat_path}")
        sys.exit(1)
    return json.loads(flat_path.read_text(encoding='utf-8'))

def apply_to_file(orig_path: Path, flat: dict):
    """
    Read the nested original JSON, replace any wordDataArray[*]['str']
    whose key (labelName_idx) exists in flat, then overwrite the original.
    """
    data = json.loads(orig_path.read_text(encoding='utf-8'))
    updated = 0

    for label in data.get("labelDataArray", []):
        label_name = label.get("labelName", "")
        for idx, word in enumerate(label.get("wordDataArray", [])):
            key = f"{label_name}_{idx}"
            if key in flat:
                word["str"] = flat[key]
                updated += 1

    # backup original
    bak_path = orig_path.with_suffix(orig_path.suffix + ".bak.json")
    orig_path.rename(bak_path)

    # write updated file
    orig_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"[OK] Applied {updated} translations to {orig_path}")
    print(f"[INFO] Original backed up as {bak_path}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python insert_str.py <path/to/classified_Files/.../file.json>")
        sys.exit(1)

    orig_path = Path(sys.argv[1])
    if not orig_path.is_file():
        print(f"[ERROR] File not found: {orig_path}")
        sys.exit(1)

    # Determine matching flat JSON in git_Localize/translate
    project_root = Path(__file__).parent
    rel = orig_path.relative_to(project_root / "classified_Files")
    flat_path = project_root / "git_Localize" / "translate" / rel

    apply_to_file(orig_path, extract_translations(flat_path))

if __name__ == "__main__":
    main()
