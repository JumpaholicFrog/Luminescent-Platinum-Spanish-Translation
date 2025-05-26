#!/usr/bin/env python3
import json
import sys
from pathlib import Path


def load_flat_translations(flat_path: Path) -> dict:
    """
    Load the flat JSON of translations, which maps keys like
    "DLP_adventure_note_001_00_0" → "Translated text"
    """
    try:
        return json.loads(flat_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"[WARN] No translations found for: {flat_path}")
        return {}


def apply_translations_to_data(data: dict, flat: dict) -> int:
    """
    Given the nested JSON data, replace any wordDataArray[*]['str']
    whose key (labelName_idx) exists in flat, and return count of replacements.
    """
    updated = 0
    for label in data.get("labelDataArray", []):
        label_name = label.get("labelName", "")
        for idx, word in enumerate(label.get("wordDataArray", [])):
            key = f"{label_name}_{idx}"
            if key in flat and flat[key].strip():
                word["str"] = flat[key]
                updated += 1
    return updated


def main():
    print("=== In-place Apply Translations ===")
    inp = input("1) Enter path to your INPUT folder (nested JSONs): ").strip()
    trans = input("2) Enter path to your TRANSLATIONS folder (flat JSONs): ").strip()

    input_dir = Path(inp)
    trans_dir = Path(trans)

    # Validate
    if not input_dir.is_dir():
        print(f"[ERROR] Input folder not found: {input_dir}")
        sys.exit(1)
    if not trans_dir.is_dir():
        print(f"[ERROR] Translations folder not found: {trans_dir}")
        sys.exit(1)

    total_files = 0
    total_updates = 0

    for orig_path in input_dir.rglob("*.json"):
        rel = orig_path.relative_to(input_dir)
        flat_path = trans_dir / rel

        # Load original
        data = json.loads(orig_path.read_text(encoding="utf-8"))
        flat = load_flat_translations(flat_path)
        updated = apply_translations_to_data(data, flat)

        if updated > 0:
            # Backup original
            bak_path = orig_path.with_suffix(orig_path.suffix + ".bak.json")
            orig_path.rename(bak_path)
            # Write updated file
            orig_path.write_text(
                json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            print(f"[{rel}] → applied {updated} translations (backup: {bak_path.name})")
        else:
            print(f"[{rel}] → no translations to apply")

        total_files += 1
        total_updates += updated

    print(
        f"\nDone. Processed {total_files} files, applied {total_updates} translations in-place."
    )


if __name__ == "__main__":
    main()
