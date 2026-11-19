"""Hai luật kiểm file và hàng đợi gợi ý bất đồng lớp. Chỉ dùng thư viện chuẩn."""
import argparse
import hashlib
import json
import sys
from collections import defaultdict
from itertools import combinations
from pathlib import Path


def inside(root, name):
    path = (root / name).resolve()
    if not path.is_relative_to(root):
        raise ValueError(f"Path outside delivery: {name}")
    return path


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def file_errors(root, target, item):
    if not inside(root, item["image"]).is_file():
        return [{"type": "missing_image", "target": target}]
    for field in ("image", "label", "mask"):
        path = inside(root, item[field])
        if not path.is_file():
            raise FileNotFoundError(path)
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != item[field + "_sha256"]:
            return [{"type": "wrong_hash", "target": target}]
    return []


def write_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("delivery", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    root = args.delivery.resolve()
    outputs = [args.out.resolve()]
    if len(set(outputs)) != len(outputs) or any(p.is_relative_to(root) for p in outputs):
        parser.error("Use distinct output files outside delivery")
    manifest = read_json(inside(root, "manifest.json"))["items"]
    errors = []
    for target, item in manifest.items():
        errors.extend(file_errors(root, target, item))
    write_json(args.out, {"errors": errors})
    print(f"{len(manifest)} images; {len(errors)} missing_image/wrong_hash")


if __name__ == "__main__":
    main()
