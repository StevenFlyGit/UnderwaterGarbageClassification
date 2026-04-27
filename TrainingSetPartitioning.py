import os
import random
import shutil

# ================= 配置区 =================
src_img_dir = './dataset/2023认领一个潜点水下垃圾照片 (水下&陆地,已脱敏)'    # 原始图片根目录（包含子文件夹）
src_txt_dir = './dataset/label'    # 所有 txt 标签放在该目录，文件名与图片同名（不含扩展名）
save_dir = 'dataset/splitData'       # 自动生成的输出路径
split_ratio = 0.9                  # 训练集占比
# ==========================================

ALLOWED_EXTS = ('.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff')


def split_data():
    # 创建目标目录结构
    for sub in ['train', 'val']:
        os.makedirs(os.path.join(save_dir, 'images', sub), exist_ok=True)
        os.makedirs(os.path.join(save_dir, 'labels', sub), exist_ok=True)

    # 递归收集图片文件（保留原始路径信息）
    entries = []
    # os.walk() 递归遍历目录，返回一个生成器，生成器每次迭代返回一个三元组 (root, dirs, files)，其中 root 是当前目录路径，dirs 是当前目录下的子目录列表，files 是当前目录下的文件列表
    for root, dirs, files in os.walk(src_img_dir): 
        for filename in files:
            if filename.lower().endswith(ALLOWED_EXTS):
                fullpath = os.path.join(root, filename)
                name, ext = os.path.splitext(filename)
                rel = os.path.relpath(fullpath, src_img_dir)
                entries.append({'img_path': fullpath, 'orig_name': name, 'ext': ext, 'rel': rel})

    if not entries:
        print(f"在 {src_img_dir} 中未找到图片文件，检查路径或扩展名。")
        return

    print(f"找到 {len(entries)} 张图片（包含子目录），准备分集...")
    print(entries[:5])  # 打印前5条记录检查路径和文件名是否正确解析

    # 处理同名文件（不同子目录）——为避免覆盖，按出现顺序给重复基名添加后缀
    name_counters = {}
    prepared = [] # 包含所有图片的列表，每个元素是一个字典，包含原始路径、原始基名、扩展名、相对路径和最终目标文件名（dest_name）等信息
    for e in entries:
        base = e['orig_name']
        count = name_counters.get(base, 0)
        if count == 0:
            dest_name = base
        else:
            # 出现重复时，添加后缀 _1, _2 等
            print(f"发现同名文件: {base}，已出现 {count} 次，生成目标文件名: {base}_{count}")
            dest_name = f"{base}_{count}"
        name_counters[base] = count + 1
        e['dest_name'] = dest_name
        prepared.append(e)

    print(f"处理同名文件后，准备分集的图片列表（前5条）:")
    print(prepared[:5])  # 再次检查前5条记录，确认 dest_name 是否正确生成

    random.seed(42)  # 固定随机种子，确保可复现
    random.shuffle(prepared)

    train_count = int(len(prepared) * split_ratio)

    for i, item in enumerate(prepared):
        subset = 'train' if i < train_count else 'val'

        # 复制图片到目标文件夹（平铺，不保留子目录），保留扩展名
        img_dst = os.path.join(save_dir, 'images', subset, item['dest_name'] + item['ext'])
        try:
            shutil.copy2(item['img_path'], img_dst)
        except Exception as ex:
            print(f"复制图片失败: {item['img_path']} -> {img_dst}，错误: {ex}")

        # 复制并重命名标签（如果存在）
        txt_src = os.path.join(src_txt_dir, item['orig_name'] + '.txt')
        txt_dst = os.path.join(save_dir, 'labels', subset, item['dest_name'] + '.txt')
        if os.path.exists(txt_src):
            try:
                shutil.copy2(txt_src, txt_dst)
            except Exception as ex:
                print(f"复制标签失败: {txt_src} -> {txt_dst}，错误: {ex}")
        else:
            print(f"警告：未找到对应标签文件 {txt_src}，跳过标签复制。")

    print(f"分集完成！训练集: {train_count} 张, 验证集: {len(prepared)-train_count} 张")


if __name__ == "__main__":
    split_data()