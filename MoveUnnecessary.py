# from ultralytics import YOLO
# model = YOLO(".\models\yolov8m.pt")
# with open("classes.txt", "w") as f:
#     for i, name in model.names.items():
#         f.write(name + "\n")

# print(1)




from pathlib import Path
import shutil
import argparse


def build_label_set(label_dir: Path) -> set:
    if not label_dir.exists():
        return set()
    return {p.stem for p in label_dir.iterdir() if p.is_file()} # 返回一个包含所有标签文件名（不带扩展名）的集合
    # stem属性返回文件名（不带扩展名），iterdir()方法返回目录下的所有文件和文件夹的路径对象，is_file()方法判断路径对象是否是一个文件

def move_unmatched(source_dir: Path, label_dir: Path, out_dir: Path, dry_run: bool = False):
    labels = build_label_set(label_dir)
    source_dir = source_dir.resolve()
    out_dir = out_dir.resolve()
    moved = 0
    skipped = 0

    for p in source_dir.rglob('*'): # 递归扫描所有文件和文件夹
        if not p.is_file():
            continue
        if p.stem in labels:
            skipped += 1
            continue

        # preserve relative path under out to avoid name collisions
        rel = p.relative_to(source_dir)
        target = out_dir / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        if dry_run:
            print(f"[DRY] Move: {p} -> {target}")
        else:
            shutil.move(str(p), str(target))
            print(f"Moved: {p} -> {target}")
        moved += 1

    print(f"Done. moved={moved}, kept={skipped}")


def main():
    parser = argparse.ArgumentParser(description='Move files not matched by label list to out folder')
    parser.add_argument('--source', default=r"E:\\StevenWork\\2023认领一个潜点水下垃圾照片 (水下&陆地,已脱敏)", help='source root to scan')
    parser.add_argument('--label', default=r"E:\\StevenWork\\label", help='label folder to compare filenames (no extension)')
    parser.add_argument('--out', default=r"E:\\StevenWork\\out", help='destination out folder')
    parser.add_argument('--dry', action='store_true', help='dry run (do not move files)')
    args = parser.parse_args()

    src = Path(args.source)
    lbl = Path(args.label)
    out = Path(args.out)

    out.mkdir(parents=True, exist_ok=True)

    if not src.exists():
        print(f"Source not found: {src}")
        return

    move_unmatched(src, lbl, out, dry_run=args.dry)


if __name__ == '__main__':
    main()


