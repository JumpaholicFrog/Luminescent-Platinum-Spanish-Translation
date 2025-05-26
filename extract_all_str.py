#!/usr/bin/env python3
import json
import sys
from pathlib import Path


def extract_str_fields(input_file: Path) -> dict:
    """
    Given one nested JSON file, return a flat dict of { "<labelName>_<idx>": "<str>" }.
    """
    data = json.loads(input_file.read_text(encoding="utf-8"))
    flat = {}
    for label in data.get("labelDataArray", []):
        label_name = label.get("labelName")
        for idx, word in enumerate(label.get("wordDataArray", [])):
            text = word.get("str")
            if text is not None:
                key = f"{label_name}_{idx}"
                flat[key] = text
    return flat


def build_gitlocalize(src_root: Path, dst_root: Path, subfolder: str):
    """
    Read every JSON under src_root/<subfolder>, extract str-fields,
    and write flat JSONs under dst_root/<subfolder> preserving filenames.
    """
    src_dir = src_root / subfolder
    dst_dir = dst_root / subfolder

    if not src_dir.exists():
        raise FileNotFoundError(f"Source folder not found: {src_dir}")

    # ensure output dir
    dst_dir.mkdir(parents=True, exist_ok=True)

    for json_path in src_dir.rglob("*.json"):
        rel = json_path.relative_to(src_dir)
        flat = extract_str_fields(json_path)

        out_file = dst_dir / rel
        out_file.parent.mkdir(parents=True, exist_ok=True)
        out_file.write_text(
            json.dumps(flat, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"Extracted {len(flat)} entries → {out_file}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python extract_all.py <subfolder_name>")
        print("Example: python extract_all.py translate")
        sys.exit(1)

    folder = sys.argv[1]  # e.g. "translate", "review", "completed", "noStrings"
    PROJECT_ROOT = Path(__file__).parent
    CLASSIFIED = PROJECT_ROOT / "classified_Files"
    GITLOCALIZE = PROJECT_ROOT / "git_Localize"

    build_gitlocalize(CLASSIFIED, GITLOCALIZE, folder)

    print("\nDone. Your GitLocalize-ready files live under:")
    print(f"  {GITLOCALIZE}/{folder}/")
