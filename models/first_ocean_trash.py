# 1. 继承你上传的官方 YOLOv8m 配置文件
_base_ = './yolov8_m_syncbn_fast_8xb16-500e_coco.py'
# 如何看出继承关系
# 在配置文件中，通过 _base_ 变量指定继承的基类配置文件
# 该配置文件会被解析器加载并执行，解析器会先加载 _base_ 指定的配置文件（如果有的话），然后再加载当前配置文件。
# 解析器会按照继承关系的顺序加载配置文件，先加载基类配置文件，再加载子类配置文件。子类配置文件中的参数会覆盖基类配置文件中的同名参数。
# 例如，在当前配置文件中，我们指定了 _base_ = './yolov8_s_syncbn_fast_8xb16-500e_coco.py'，
# 这意味着当前配置文件会继承 './yolov8_s_syncbn_fast_8xb16-500e_coco.py' 中定义的所有参数。我
# 们在当前配置文件中修改了部分参数，这些修改会覆盖基类配置文件中的同名参数，而未修改的参数则会保持不变，继续使用基类配置文件中的值。


# ======================== 必须修改的配置 ======================
# 2. 定义你的海洋垃圾类别名称（从文件读取，文件每行一个类别）
# import os

# # 指定类别文件路径（按需修改）
# _classes_file = r'E:\\StevenWork\\UnderwaterGarbageClassification\\dataset\\classes.txt'
# if not os.path.isabs(_classes_file): # 如果不是绝对路径，则相对于当前配置文件所在目录
#     _classes_file = os.path.join(os.path.dirname(__file__), _classes_file)

# try:
#     with open(_classes_file, 'r', encoding='utf-8') as f:
#         print(f'Loading classes from {_classes_file}...')

#         # 去掉空行并移除每行首尾空白
#         class_name = tuple(line.strip() for line in f if line.strip()) # 第一个strip()去掉行首行尾空白，第二个strip()过滤掉空行
#         # 该简化写法等同于
#         # class_name = tuple()
#         # for line in f:
#         #     line = line.strip()
#         #     if line:  # 只添加非空行
#         #         # 添加元素到元组
#         #         class_name += (line,) # 和 class_name = class_name + (line,) 等价，都是创建一个新的元组并赋值给 class_name， 因为元组是不可变类型，不能直接修改，所以只能通过拼接的方式创建一个新的元组。
        
# except Exception:
#     # 兜底：如果读取失败则使用空元组，避免抛异常中断配置解析
#     class_name = tuple()
#     # 打印具体异常信息，帮助调试    
#     import traceback
#     print(f'Warning: Failed to read classes from {_classes_file}. Using empty class list.', )
#     print(f'Error reading classes from {_classes_file}: {traceback.format_exc()}')


class_name=('beer bottle', 'tire', 'plastic shell', 'gunny sack', 'plastic bottle', 'can', 'fishing gear', 'ointment', 'plastic bag', 'plastic packaging bag', 'glove', 'ground cage', 'fishing net')
num_classes = len(class_name)
metainfo = dict(classes=class_name)

print(f'Loaded {num_classes} classes: {class_name}')

# 3. 指定你刚刚划分好的数据集路径
data_root = 'E:\\StevenWork\\UnderwaterGarbageClassification\\dataset\\splitData\\' # 这里填你存放 images 和 labels 的根目录
train_ann_file = 'annotations\\annotationsCocoTrain.json' # 训练集 JSON 标注路径（相对 data_root）
train_data_prefix = 'images\\train\\'       # 训练集图片目录（相对 data_root）
val_ann_file = 'annotations\\annotationsCocoVal.json'     # 验证集 JSON 标注路径
val_data_prefix = 'images\\val\\'           # 验证集图片目录

# ======================== 覆盖模型与数据配置 ======================
# 4. 修改模型输出头的类别数（覆盖 _base_ 里的默认 80 类）
model = dict(
    bbox_head=dict(
        head_module=dict(num_classes=num_classes)
    )
)
# Ensure the assigner (used to generate targets) also uses the same num_classes
# (base config may have captured num_classes=80), so override it here.
model.setdefault('train_cfg', {})
model['train_cfg'].setdefault('assigner', {})
model['train_cfg']['assigner']['num_classes'] = num_classes

# 5. 覆盖训练集 DataLoader
train_dataloader = dict(
    batch_size=20, # 如果显存够大，可以调大到 32 或 64
    dataset=dict(
        type='YOLOv5CocoDataset',
        data_root=data_root,
        metainfo=metainfo,
        ann_file=train_ann_file,
        data_prefix=dict(img=train_data_prefix)
    )
)

# 6. 覆盖验证集 DataLoader
val_dataloader = dict(
    dataset=dict(
        type='YOLOv5CocoDataset',
        data_root=data_root,
        metainfo=metainfo,
        ann_file=val_ann_file,
        data_prefix=dict(img=val_data_prefix)
    )
)
test_dataloader = val_dataloader

# 7. 覆盖评估器配置
val_evaluator = dict(ann_file=data_root + val_ann_file)
test_evaluator = val_evaluator

# ======================== 关键：迁移学习 ======================
# 8. 加载官方在 COCO 上训练好的权重。这能让你的模型站在巨人的肩膀上，在174张图上也能快速收敛。
load_from = 'E:\\StevenWork\\UnderwaterGarbageClassification\\models\\yolov8_m_mask-refine_syncbn_fast_8xb16-500e_coco_20230216_223400-f40abfcd.pth'