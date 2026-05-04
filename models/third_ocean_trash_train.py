# 1. 继承你上传的官方 YOLOv8m 配置文件
_base_ = './yolov8_s_syncbn_fast_8xb16-500e_coco.py'
# 如何看出继承关系
# 在配置文件中，通过 _base_ 变量指定继承的基类配置文件
# 该配置文件会被解析器加载并执行，解析器会先加载 _base_ 指定的配置文件（如果有的话），然后再加载当前配置文件。
# 解析器会按照继承关系的顺序加载配置文件，先加载基类配置文件，再加载子类配置文件。子类配置文件中的参数会覆盖基类配置文件中的同名参数。
# 例如，在当前配置文件中，我们指定了 _base_ = './yolov8_s_syncbn_fast_8xb16-500e_coco.py'，
# 这意味着当前配置文件会继承 './yolov8_s_syncbn_fast_8xb16-500e_coco.py' 中定义的所有参数。我
# 们在当前配置文件中修改了部分参数，这些修改会覆盖基类配置文件中的同名参数，而未修改的参数则会保持不变，继续使用基类配置文件中的值。


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

# 将训练轮数改为 100（按需修改数字）
max_epochs = 200

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

# 修改学习率调度器，增加预热阶段和余弦退火衰减
train_cfg = dict(
    type='EpochBasedTrainLoop', 
    max_epochs=max_epochs, 
    val_interval=10 # 每10轮验证一次
)

# ======================== 修复学习率接管问题 ======================

# 必须使用 _delete_=True 来彻底删除父配置文件中 YOLOv5ParamSchedulerHook 的残留参数
# 否则会触发 TypeError: ParamSchedulerHook() takes no arguments
default_hooks = dict(
    param_scheduler=dict(type='ParamSchedulerHook', _delete_=True)
)
# 要让列表形式的自定义 param_scheduler 真正在每一轮生效，
# 我们需要将更新学习率的钩子替换回 MMEngine 原生的标准钩子。
# 也就是把它设为 dict(type='ParamSchedulerHook')。
# 这样，标准钩子每当训练到新阶段时，就会自动去读取您写好的预热和余弦退火配置。

# 标准的 ParamSchedulerHook 本身非常纯粹，它的逻辑是直接去配置文件根目录找 
# param_scheduler 变量，因此它初始化时不需要（也不允许）传递复杂的业务参数。


# 显式声明作用域
default_scope = 'mmyolo'

# 自定义的 param_scheduler 才会真正生效
param_scheduler = [
    # 第一部分：预热阶段 (Warmup)
    dict(
        type='LinearLR',  # 线性预热
        start_factor=0.0001, # 初始学习率倍率
        by_epoch=True,       # 按轮次计算
        begin=0,             # 从第 0 轮开始
        end=15),              # 到第 15 轮结束
    
    # 第二部分：正式训练阶段 (Decay)
    dict(
        type='CosineAnnealingLR', # 余弦退火衰减
        eta_min=0.0001,           # 训练结束时的最低学习率
        begin=15,                  # 从第 15 轮开始（接续预热）
        end=max_epochs,           # 到你设定的 200 轮结束
        T_max=max_epochs,         # 整个余弦周期的跨度
        by_epoch=True,
        convert_to_iter_based=True) # 细化到每一次迭代都平滑下降
]


# 5. 覆盖训练集 DataLoader
train_dataloader = dict(
    batch_size=30, # 如果显存够大，可以调大到 32 或 64
    dataset=dict(
        type='YOLOv5CocoDataset', # 确保使用适合 COCO 格式的 Dataset 类
        data_root=data_root, # 这里填你存放数据集的根目录
        metainfo=metainfo, # 类别信息
        ann_file=train_ann_file, # 训练集 JSON 标注路径（相对 data_root）
        data_prefix=dict(img=train_data_prefix) # 训练集图片目录（相对 data_root）
    )
)

# 6. 覆盖验证集 DataLoader
val_dataloader = dict(
    dataset=dict(
        type='YOLOv5CocoDataset', # 确保使用适合 COCO 格式的 Dataset 类
        data_root=data_root, # 这里填你存放数据集的根目录
        metainfo=metainfo, # 类别信息
        ann_file=val_ann_file, # 验证集 JSON 标注路径（相对 data_root）
        data_prefix=dict(img=val_data_prefix) # 验证集图片目录（相对 data_root）
    )
)
test_dataloader = val_dataloader

# 7. 覆盖评估器配置
val_evaluator = dict(ann_file=data_root + val_ann_file) # 验证集 JSON 标注路径（绝对路径）
test_evaluator = val_evaluator

# ======================== 关键：迁移学习 ======================
# 8. 加载官方在 COCO 上训练好的权重。建议本地下载后使用本地路径，如果直接使用远程链接可能会因为网络问题导致下载失败。
load_from = 'E:\\StevenWork\\UnderwaterGarbageClassification\\models\\yolov8_s_mask-refine_syncbn_fast_8xb16-500e_coco_20230216_095938-ce3c1b3f.pth'

# Print effective configuration at parse time so you can verify overrides
print('===== ocean_trash.py configuration summary =====')
print(f' num_classes = {num_classes}')
print(f' max_epochs = {max_epochs}')
# try to print train batch size if present
try:
    tb = train_dataloader.get('batch_size', 'N/A') if isinstance(train_dataloader, dict) else getattr(train_dataloader, 'batch_size', 'N/A')
except Exception:
    tb = 'N/A'
print(f' train_dataloader.batch_size = {tb}')
print(f" base_lr = {globals().get('base_lr', 'N/A')}")
print(f" load_from = {load_from}")
print('===============================================')