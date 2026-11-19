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


def overlap(a, b):
    x, y, w, h = a
    u, v, s, t = b
    area = max(0, min(x+w, u+s)-max(x, u)) * max(0, min(y+h, v+t)-max(y, v))
    union = w*h + s*t - area
    return area / union if union > 0 else 0


def mask_samples(width, height, rgb, segment_ids):
    points = defaultdict(list)
    for y in range(1, height, 3):
        for x in range(1, width, 3):
            k = (y * width + x) * 3
            segment_id = rgb[k] | rgb[k+1] << 8 | rgb[k+2] << 16
            if segment_id in segment_ids:
                points[segment_id].append((x, y))
    return points


def hits(point, box):
    x, y, w, h = box
    return x <= point[0] < x+w and y <= point[1] < y+h


def region_hint(segment, name, points, detections):
    """Rank hints within one image; the reviewer decides whether the hint is real."""
    if len(points) < 35:
        return None
    bounds = segment["bbox"]
    matches = []
    for label, box in detections:
        iou = overlap(bounds, box)
        if iou <= 0:
            continue
        count = sum(hits(point, box) for point in points)
        matches.append((count / len(points), iou, label, box))
    same = [m for m in matches if m[2] == name]
    for a, b in combinations(same, 2):
        if min(a[0], b[0]) >= .23 and overlap(a[3], b[3]) < .12:
            joint = sum(hits(pt, a[3]) or hits(pt, b[3]) for pt in points) / len(points)
            if joint > .85 and max(a[0], b[0]) < .77:
                return (3 + joint, "instance_merge", "Một vùng mask trải trên hai box cùng lớp.", [a[3], b[3]], name)
    for cover, iou, label, box in sorted(matches, reverse=True):
        if label != name and iou >= .65 and cover >= .75 and not any(m[1] >= .55 for m in same):
            return (3 + iou, "class_disagreement", "Box và mask ở cùng vị trí nhưng khác tên lớp.", [box], label)
    if not any(m[0] >= .15 or m[1] >= .15 for m in matches) and len(points) >= 100:
        return (2.5, "missing_box", "Mask của vật khá lớn nhưng không thấy box tương ứng.", [], "—")
    if same:
        cover, iou, label, box = max(same, key=lambda m: m[1])
        if .25 <= iou < .78 and .25 <= cover < .79:
            return (1 + iou, "bbox_drift", f"Khoảng {1-cover:.0%} điểm mask lấy mẫu nằm ngoài box cùng lớp.", [box], label)
    return None


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
