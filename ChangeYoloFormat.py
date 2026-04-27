#!/usr/bin/env python3
"""
convert_yolo_to_coco.py

将 YOLO txt 标签（dataset/label）转换为 COCO 格式 JSON。

用法示例:
python convert_yolo_to_coco.py --labels-dir dataset/label --images-dir dataset --classes-file classes.txt --output annotations_coco.json
"""
import os
import json
import argparse
import glob
from PIL import Image


def find_images(images_dir, exts):
    mapping = {}
    for root, _, files in os.walk(images_dir):
        for f in files:
            name, ext = os.path.splitext(f) # os.path.splitext() 将文件名分割成两部分：文件名（不含扩展名）和扩展名
            if ext.lower() in exts:
                mapping.setdefault(name, []).append(os.path.join(root, f)) 
                # append() 方法用于在列表末尾添加新的元素，setdefault() 方法用于获取指定键的值，如果键不存在则将其设置为默认值（这里是一个空列表）并返回该值。这样可以确保 mapping 字典中的每个键（文件名）都对应一个列表，即使只有一个图像文件也会被放在一个列表中。
    return mapping # 返回一个字典，键是文件名（不含扩展名），值是一个列表，包含所有具有该基名的图像文件的完整路径（可能有多个同名文件在不同子目录下）


def load_classes(classes_file):
    if not classes_file or not os.path.exists(classes_file):
        return []
    with open(classes_file, encoding='utf-8') as f:
        lines = [l.strip() for l in f.readlines() if l.strip()]
    return lines


def convert(labels_dir, images_dir, classes_file, output, exts):
    exts = set(e.lower() if e.startswith('.') else f'.{e.lower()}' for e in exts)
    images_map = find_images(images_dir, exts)
    classes = load_classes(classes_file)

    images = []
    annotations = []
    ann_id = 0
    img_id = 0

    # 打印图片文件数量
    print(f"在 {images_dir} 中找到 {sum(len(v) for v in images_map.values())} 张图片，准备转换...")
    
    label_paths = sorted(glob.glob(os.path.join(labels_dir, '*.txt')))
    for label_path in label_paths:
        base = os.path.splitext(os.path.basename(label_path))[0]
        candidates = images_map.get(base) # 获取与标签文件同名的图像文件列表（可能有多个同名文件在不同子目录下）
        if not candidates:
            print(f"跳过：未找到对应图像 -> {base} (标签文件 {label_path})")
            continue
        if len(candidates) > 1:
            print(f"警告：找到多个同名图像，使用第一个 -> {candidates[0]}")
        img_path = candidates[0]
        try:
            with Image.open(img_path) as im:
                width, height = im.size
        except Exception as e:
            print(f"无法打开图像 {img_path}: {e}")
            continue

        rel_path = os.path.relpath(img_path, images_dir).replace('\\', '/')
        images.append({
            'id': img_id,
            'file_name': rel_path,
            'width': width,
            'height': height,
        })

        with open(label_path, encoding='utf-8') as lf:
            lines = [l.strip() for l in lf.readlines() if l.strip()]
        for line in lines:
            parts = line.split()
            if len(parts) < 5:
                print(f"跳过非法行 ({label_path}): {line}")
                continue
            try:
                cls = int(parts[0])
                x_c, y_c, w_n, h_n = map(float, parts[1:5])
            except Exception as e:
                print(f"解析错误 ({label_path}): {line} -> {e}")
                continue

            bbox_w = w_n * width
            bbox_h = h_n * height
            x_min = (x_c - w_n / 2.0) * width
            y_min = (y_c - h_n / 2.0) * height

            # clamp
            x_min = max(0, x_min)
            y_min = max(0, y_min)
            bbox_w = max(0, min(bbox_w, width - x_min))
            bbox_h = max(0, min(bbox_h, height - y_min))

            category_id = cls  # COCO category ids start at 0

            ann = {
                'id': ann_id,
                'image_id': img_id,
                'category_id': category_id,
                'bbox': [round(x_min, 2), round(y_min, 2), round(bbox_w, 2), round(bbox_h, 2)],
                'area': round(bbox_w * bbox_h, 2),
                'iscrowd': 0,
                'segmentation': [],
            }
            annotations.append(ann)
            ann_id += 1

        img_id += 1

    categories = []
    for i, name in enumerate(classes):
        categories.append({'id': i + 1, 'name': name})

    coco = {
        'images': images,
        'annotations': annotations,
        'categories': categories,
    }

    with open(output, 'w', encoding='utf-8') as out:
        json.dump(coco, out, ensure_ascii=False, indent=2)

    print(f"完成：生成 COCO 标注 -> {output}")


def parse_args():
    p = argparse.ArgumentParser(description='Convert YOLO txt labels to COCO json')
    p.add_argument('--labels-dir', default='./dataset/splitData/labels/train', help='目录，包含 YOLO txt 标签')
    p.add_argument('--images-dir', default='./dataset/splitData/images/train', help='图片根目录，递归搜索对应图像')
    p.add_argument('--classes-file', default='./dataset/classes.txt', help='每行一个类别名的文件')
    p.add_argument('--output', default='annotationsCocoTrain.json', help='输出 COCO json 文件路径')
    p.add_argument('--exts', nargs='+', default=['.jpg', '.jpeg', '.png'], help='可识别的图片后缀')
    return p.parse_args()


if __name__ == '__main__':
    args = parse_args()
    convert(args.labels_dir, args.images_dir, args.classes_file, args.output, args.exts)
