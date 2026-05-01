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


# ======================== 覆盖模型推理配置 ======================

# 4. 修改模型输出头的类别数（覆盖 _base_ 里的默认 80 类）
model = dict(
    bbox_head=dict(
        head_module=dict(num_classes=num_classes)
    )
)


