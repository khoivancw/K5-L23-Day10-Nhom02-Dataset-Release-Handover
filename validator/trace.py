"""Trace a ticket using the scenes, class and old guideline identified by the reviewer."""
import argparse
import csv
from pathlib import Path

from validate import inside, read_json, write_json


def trace(root, scenes, class_name, guideline):
    items = read_json(inside(root, "manifest.json"))["items"]
    metadata = read_json(inside(root, "metadata.json"))["items"]
    with inside(root, "jobs.csv").open(encoding="utf-8-sig", newline="") as stream:
        jobs = {row["job_id"]: row for row in csv.DictReader(stream)}
    classes = {}
    for line in inside(root, "classes.txt").read_text(encoding="utf-8").splitlines():
        if line.strip():
            class_id, name = line.split(maxsplit=1)
            classes[name] = class_id
    if class_name not in classes:
        raise ValueError(f"Unknown detection class: {class_name}")
    if guideline not in {job["guideline"] for job in jobs.values()}:
        raise ValueError(f"Unknown job guideline: {guideline}")
    unknown = scenes - {row["scene_id"] for row in metadata}
    if unknown:
        raise ValueError(f"Unknown scenes: {sorted(unknown)}")

    tier_a, tier_b, notify = [], [], set()
    for row in metadata:
        image = row["image"]
        job = jobs[row["job_id"]]
        if job["guideline"] != guideline:
            continue
        labels = inside(root, items[image]["label"]).read_text(encoding="utf-8")
        boxes = (line.split() for line in labels.splitlines())
        if any(len(box) == 5 and box[0] == classes[class_name] for box in boxes):
            tier = tier_a if row["scene_id"] in scenes else tier_b
            tier.append(image)
            notify.update((job["annotator"], job["reviewer"]))
    return dict(tier_a=sorted(tier_a), tier_b=sorted(tier_b), notify=sorted(notify))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("delivery", type=Path)
    parser.add_argument("--scenes", nargs="+", required=True)
    parser.add_argument("--class-name", required=True)
    parser.add_argument("--guideline", required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    root = args.delivery.resolve()
    if args.out.resolve().is_relative_to(root):
        parser.error("Write trace.json outside delivery")
    result = trace(root, set(args.scenes), args.class_name, args.guideline)
    write_json(args.out, result)
