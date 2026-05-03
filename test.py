from pathlib import Path

root = Path(r"E:\StevenWork\已脱敏水下垃圾-水下&陆地照片")
target_text = "水下垃圾照片 "

renamed_count = 0
skipped_count = 0

for file_path in root.rglob("*"):
    if not file_path.is_file():
        continue

    old_name = file_path.name
    if target_text not in old_name:
        print(f"跳过（未找到目标文本）: {old_name}")
        continue

    new_name = old_name.replace(target_text, "")
    new_path = file_path.with_name(new_name)

    if new_path.exists():
        print(f"跳过（目标已存在）: {new_path}")
        skipped_count += 1
        continue

    file_path.rename(new_path)
    print(f"已重命名: {file_path} -> {new_path}")
    renamed_count += 1

print(f"\n完成：重命名 {renamed_count} 个文件，跳过 {skipped_count} 个文件。")