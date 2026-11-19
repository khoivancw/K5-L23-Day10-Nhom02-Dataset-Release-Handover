"""Validate delivery files, detection labels, panoptic segments and release metadata."""
import argparse
import csv
import hashlib
import json
import sys
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from pngutil import read_rgb


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


def label_errors(path, classes, width, height):
    issues = set()
    groups = defaultdict(list)
    # YOLO stores six decimal places. Allow rounding at the image border.
    epsilon = 0.000002
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        label, *coordinates = line.split()
        if label not in classes:
            issues.add("invalid_class")
        cx, cy, w, h = map(float, coordinates)
        if not (w > 0 and h > 0 and cx-w/2 >= -epsilon and cy-h/2 >= -epsilon
                and cx+w/2 <= 1+epsilon and cy+h/2 <= 1+epsilon):
            issues.add("bbox_out_of_bounds")
        for x, y, other_w, other_h in groups[label]:
            if (abs(w-other_w) <= epsilon and abs(h-other_h) <= epsilon
                    and abs(cx-x)*width <= 2.001 and abs(cy-y)*height <= 2.001):
                issues.add("duplicate_box")
                break
        groups[label].append((cx, cy, w, h))
    return issues


def metadata_errors(root):
    with inside(root, "jobs.csv").open(encoding="utf-8-sig", newline="") as stream:
        guidelines = {row["job_id"]: row["guideline"] for row in csv.DictReader(stream)}
    errors = []
    splits = defaultdict(set)
    for row in read_json(inside(root, "metadata.json"))["items"]:
        splits[row["scene_id"]].add(row["split"])
        if row["guideline_version"] != guidelines[row["job_id"]]:
            errors.append({"type": "guideline_mismatch", "target": row["image"]})
    errors.extend({"type": "scene_leak", "target": scene}
                  for scene, values in splits.items() if len(values) > 1)
    return errors


def validate_rules(root, manifest):
    pan = read_json(inside(root, "panoptic.json"))
    images = {i["id"]: i for i in pan["images"]}
    categories = {c["id"]: c for c in pan["categories"]}
    annotations = {a["file_name"]: a for a in pan["annotations"]}
    classes = {line.split()[0] for line in inside(root, "classes.txt").read_text().splitlines() if line.strip()}
    errors = metadata_errors(root)
    for target, item in manifest.items():
        errors.extend(file_errors(root, target, item))
        ann = annotations[Path(item["mask"]).name]
        im = images[ann["image_id"]]
        issues = label_errors(inside(root, item["label"]), classes, im["width"], im["height"])
        _, _, rgb = read_rgb(inside(root, item["mask"]))
        pixels = iter(rgb)
        counts = Counter(zip(pixels, pixels, pixels))
        for segment in ann["segments_info"]:
            category = categories.get(segment["category_id"])
            if category is None:
                issues.add("invalid_category_id")
            elif category["isthing"] and segment["id"] and not segment.get("iscrowd"):
                key = segment["id"]
                actual_area = counts[(key & 255, key >> 8 & 255, key >> 16 & 255)]
                if actual_area < segment["area"]:
                    issues.add("thing_overlap")
        errors.extend({"type": issue, "target": target} for issue in sorted(issues))
    return errors


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


def suggest(root, manifest):
    pan = read_json(inside(root, "panoptic.json"))
    images = {i["id"]: i for i in pan["images"]}
    categories = {c["id"]: c for c in pan["categories"]}
    names = dict(line.split(maxsplit=1) for line in inside(root, "classes.txt").read_text().splitlines() if line.strip())
    annotations = {a["file_name"]: a for a in pan["annotations"]}
    queue = []
    for target, item in manifest.items():
        if not inside(root, item["image"]).is_file():
            continue
        ann = annotations.get(Path(item["mask"]).name)
        if not ann:
            continue
        im = images[ann["image_id"]]
        segments = [s for s in ann["segments_info"] if not s.get("iscrowd")
                    and categories.get(s["category_id"], {}).get("isthing")]
        detections = []
        for line in inside(root, item["label"]).read_text().splitlines():
            fields = line.split()
            if len(fields) != 5 or fields[0] not in names:
                continue
            cx, cy, w, h = map(float, fields[1:])
            if w > 0 and h > 0:
                detections.append((names[fields[0]], [(cx-w/2)*im["width"], (cy-h/2)*im["height"],
                                                     w*im["width"], h*im["height"]]))
        width, height, rgb = read_rgb(inside(root, item["mask"]))
        points = mask_samples(width, height, rgb, {s["id"] for s in segments})
        best_score = 0
        best = None
        for seg in segments:
            category = categories[seg["category_id"]]["name"]
            hint = region_hint(seg, category, points[seg["id"]], detections)
            if hint and hint[0] > best_score:
                best_score, kind, reason, boxes, detection = hint
                regions = [seg["bbox"], *boxes]
                left = min(r[0] for r in regions)
                top = min(r[1] for r in regions)
                right = max(r[0]+r[2] for r in regions)
                bottom = max(r[1]+r[3] for r in regions)
                best = dict(target=target, hint=kind, reason=reason, boxes=boxes,
                            box=[left, top, right-left, bottom-top], detection=detection,
                            panoptic=category, segment_id=seg["id"])
        if best:
            queue.append(best)
    return queue


def write_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("delivery", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--candidates", type=Path)
    args = parser.parse_args()
    root = args.delivery.resolve()
    outputs = [p.resolve() for p in (args.out, args.candidates) if p]
    if len(set(outputs)) != len(outputs) or any(p.is_relative_to(root) for p in outputs):
        parser.error("Use distinct output files outside delivery")
    manifest = read_json(inside(root, "manifest.json"))["items"]
    errors = validate_rules(root, manifest)
    queue = suggest(root, manifest) if args.candidates else []
    write_json(args.out, {"errors": errors})
    print(f"{len(manifest)} images; {len(errors)} rule findings")
    if args.candidates:
        write_json(args.candidates, {"candidates": queue})
        print(f"{len(queue)} images for visual review")


if __name__ == "__main__":
    main()
