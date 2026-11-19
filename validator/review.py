"""Xem ảnh gốc, khung detection và viền mask. Người xem tự ghi kết luận."""
import argparse
import csv
import os
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageTk

from validate import inside, read_json

FIELDS = ["image", "type", "verdict", "note"]
TYPES = ("class_swap", "category_swap", "bbox_drift", "missing_box", "instance_merge")


def render(root, item, candidate, overlays):
    with Image.open(inside(root, item["image"])) as photo:
        frame = photo.convert("RGB")
    if overlays:
        with Image.open(inside(root, item["mask"])) as png:
            rgb = png.convert("RGB")
        if candidate:
            region = candidate["segment_id"]
            selected = tuple((region >> shift) & 255 for shift in (0, 8, 16))
            channels = [c.point([255 if v == k else 0 for v in range(256)])
                        for c, k in zip(rgb.split(), selected)]
            mask = ImageChops.darker(ImageChops.darker(channels[0], channels[1]), channels[2])
            edge = ImageChops.subtract(mask, mask.filter(ImageFilter.MinFilter(5)))
            boxes = candidate.get("boxes", [candidate["box"]])
        else:
            edge = Image.new("L", frame.size)
            for c in rgb.split():
                diff = ImageChops.subtract(c.filter(ImageFilter.MaxFilter(3)), c.filter(ImageFilter.MinFilter(3)))
                edge = ImageChops.lighter(edge, diff)
            edge = edge.point([0] + [255]*255)
            boxes = []
            for line in inside(root, item["label"]).read_text().splitlines():
                if line.strip():
                    _, cx, cy, w, h = map(float, line.split())
                    boxes.append(((cx-w/2)*frame.width, (cy-h/2)*frame.height, w*frame.width, h*frame.height))
        frame.paste((0, 235, 250), mask=edge)
        draw = ImageDraw.Draw(frame)
        for x, y, w, h in boxes:
            if w > 0 and h > 0:
                draw.rectangle((x, y, x+w, y+h), outline="orange", width=3)
    return frame


def save_review(path, target, kind, verdict, reviewer, note):
    if not reviewer.strip() or len(note.strip()) < 20 or kind not in TYPES or verdict not in ("confirmed", "rejected"):
        raise ValueError("Điền tên, loại lỗi, kết luận và mô tả ít nhất 20 ký tự về điều m thấy.")
    rows = []
    if path.exists():
        with path.open(encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames != FIELDS:
                raise ValueError("CSV đang có cấu trúc khác mẫu.")
            rows = list(reader)
    rows = [r for r in rows if r["image"] != target]
    rows.append(dict(image=target, type=kind, verdict=verdict, note=f"{reviewer.strip()}: {note.strip()}"))
    path.parent.mkdir(parents=True, exist_ok=True)
    import tempfile
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as f:
        tmp = Path(f.name)
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    try:
        os.replace(tmp, path)
    finally:
        tmp.unlink(missing_ok=True)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("delivery", type=Path)
    p.add_argument("--candidates", required=True, type=Path)
    p.add_argument("--log", required=True, type=Path)
    p.add_argument("--rules", type=Path, help="File lỗi luật, mặc định dùng rules.json cạnh candidates.json nếu có")
    args = p.parse_args()
    root = args.delivery.resolve()
    if args.log.resolve().is_relative_to(root) or args.log.resolve() == args.candidates.resolve():
        p.error("Chọn file CSV riêng bên ngoài delivery.")
    manifest = read_json(inside(root, "manifest.json"))["items"]
    queue = read_json(args.candidates)["candidates"]
    candidates = {c["target"]: c for c in queue}
    rules_path = args.rules or args.candidates.with_name("rules.json")
    if args.rules and not rules_path.is_file():
        p.error(f"Không tìm thấy {rules_path}")
    rules = {}
    if rules_path.is_file():
        for err in read_json(rules_path)["errors"]:
            rules.setdefault(err["target"], []).append(err["type"])
    targets = list(manifest)
    warnings = [t for t in targets if t in candidates or t in rules]
    if not targets:
        p.exit(message="Lô rỗng.")
    index = 0
    win = tk.Tk()
    win.title("Lab 10 · Review bằng mắt")
    header = ttk.Label(win, padding=5)
    header.pack()
    picture = ttk.Label(win)
    picture.pack()
    overlays = tk.BooleanVar(value=True)
    zoom = tk.DoubleVar(value=1)
    bar = ttk.Frame(win)
    bar.pack()
    fields = ttk.Frame(win)
    fields.pack()
    name, kind, verdict, note = [tk.StringVar() for _ in range(4)]
    for title, widget in [
        ("Người xem", ttk.Entry(fields, textvariable=name, width=18)),
        ("Loại lỗi", ttk.Combobox(fields, textvariable=kind, values=TYPES, state="readonly", width=16)),
        ("Kết luận", ttk.Combobox(fields, textvariable=verdict, values=("confirmed", "rejected"), state="readonly", width=12)),
        ("Thấy gì trong ảnh?", ttk.Entry(fields, textvariable=note, width=48))]:
        col = fields.grid_size()[0]
        ttk.Label(fields, text=title).grid(row=0, column=col)
        widget.grid(row=1, column=col, padx=3)

    def refresh():
        target = targets[index]
        candidate = candidates.get(target)
        messages = []
        rule_names = {"missing_image": "Thiếu file ảnh", "wrong_hash": "Mã SHA-256 của file khác manifest"}
        for code in rules.get(target, []):
            messages.append(f"{code} · {rule_names.get(code, code)}")
        if candidate:
            reason = candidate.get("reason", "Khung và mask có tên lớp khác nhau.")
            messages.append(f'Nghi vấn: {reason} (Box: {candidate["detection"]} / Mask: {candidate["panoptic"]})')
        info = "\n".join(messages) or "Chưa có cảnh báo từ các phép kiểm đã chạy."
        header.configure(text=f"{index+1}/{len(targets)} · {target} · {len(warnings)}/{len(manifest)} ảnh có cảnh báo\n{info}",
                         foreground="#943c08" if messages else "#24453e")
        try:
            frame = render(root, manifest[target], candidate, overlays.get())
        except (OSError, ValueError) as exc:
            picture.configure(image="", text=f"Không hiển thị được ảnh hoặc lớp nhãn: {exc}")
            return
        picture.configure(text="")
        # Zoom vào vùng đang tranh chấp để quan sát trên màn hình nhỏ.
        if zoom.get() > 1 and candidate:
            x, y, w, h = candidate["box"]
            frame = frame.crop((max(0,int(x-w*.3)), max(0,int(y-h*.3)),
                                min(frame.width,int(x+w*1.3)+1), min(frame.height,int(y+h*1.3)+1)))
            frame = frame.resize((max(1,int(frame.width*2)), max(1,int(frame.height*2))))
        frame.thumbnail((min(900,win.winfo_screenwidth()-40), min(530,win.winfo_screenheight()-240)))
        picture.photo = ImageTk.PhotoImage(frame)
        picture.configure(image=picture.photo)

    def move(step):
        nonlocal index
        index = min(len(targets)-1, max(0,index+step))
        kind.set("")
        verdict.set("")
        note.set("")
        refresh()

    def change_filter():
        nonlocal targets, index
        previous = targets[index]
        targets = warnings if flagged.get() else list(manifest)
        index = targets.index(previous) if previous in targets else 0
        move(0)

    def record():
        try:
            save_review(args.log, targets[index], kind.get(), verdict.get(), name.get(), note.get())
        except (OSError, ValueError) as exc:
            messagebox.showerror("Chưa lưu", str(exc))
            return
        if index+1 < len(targets):
            move(1)
        else:
            messagebox.showinfo("Đã lưu", str(args.log))

    ttk.Button(bar, text="Ảnh trước", command=lambda: move(-1)).pack(side="left")
    ttk.Button(bar, text="Ảnh sau", command=lambda: move(1)).pack(side="left")
    ttk.Checkbutton(bar, text="Khung cam / viền mask xanh", variable=overlays, command=refresh).pack(side="left")
    ttk.Checkbutton(bar, text="Phóng vùng nghi vấn", variable=zoom, onvalue=2, offvalue=1, command=refresh).pack(side="left")
    flagged = tk.BooleanVar(value=False)
    ttk.Checkbutton(bar, text="Chỉ ảnh có cảnh báo", variable=flagged, command=change_filter,
                    state="normal" if warnings else "disabled").pack(side="left")
    ttk.Button(win, text="Lưu nhận xét", command=record).pack()
    refresh()
    win.mainloop()


if __name__ == "__main__":
    main()
