import torch;

# 查看torch版本
print(torch.__version__);
x = torch.tensor([1, 2, 3]);
print(x);


from ultralytics import YOLO

# 首次运行此行代码时，系统会自动下载 yolov8m.pt 到当前目录
model = YOLO("yolov8m.pt")


# 进行预测，参数详见：https://docs.ultralytics.com/modes/predict/#参数说明

# model.predict(source=r'E:\StevenWork\UnderwaterGarbageClassification\dataset\2023认领一个潜点水下垃圾照片 (水下&陆地,已脱敏)\202303水下垃圾-水下&陆地照片', 
#         save=True, conf=0.25, show=True, save_txt=True, save_conf=True, line_width=2, show_labels=False, show_conf=False, name='yolo_output',
#         project=r'E:\StevenWork\UnderwaterGarbageClassification\dataset\2023认领一个潜点水下垃圾照片 (水下&陆地,已脱敏)\202303水下垃圾-水下&陆地照片\yolo_output', name='yolo_output',
#         exist_ok=True, device='cuda:0' if torch.cuda.is_available() else 'cpu', classes=None, agnostic_nms=False,
#         augment=False, visualize=False, data=False, dnn=False, iou_thres=0.45, max_det=1000, amp=False, 
#         half=False, vid_stride=1, save_crop=False, save_json=False, save_frames=False, save_dir=None);

# source: 输入图像路径，可以是单个图像文件、目录、视频文件或摄像头设备
# save: 是否保存预测结果图像
# conf: 置信度阈值，只有预测结果的置信度高于该值才会被保留
# show: 是否显示预测结果图像
# save_txt: 是否保存预测结果的文本文件
# save_conf: 是否在文本文件中保存置信度信息
# line_width: 预测结果边界框的线条厚度
# show_labels: 是否隐藏预测结果的类别标签
# show_conf: 是否隐藏预测结果的置信度信息
# name: 预测结果保存的子目录名称
# project: 预测结果保存的目录, 默认是 'runs/predict'
# exist_ok: 是否允许覆盖已存在的预测结果目录
# device: 运行预测的设备，可以是 'cpu' 或 'cuda:0'
# classes: 只保留指定类别的预测结果，传入一个类别索引列表
# agnostic_nms: 是否使用类别无关的非极大值抑制, 默认是 False，即使用类别相关的非极大值抑制
# augment: 是否使用数据增强进行预测
# visualize: 是否可视化特征图
# data: 是否在预测结果中包含数据加载信息
# dnn: 是否使用 OpenCV DNN 模块进行预测, 默认是 False，即使用 PyTorch 进行预测, 使用 OpenCV DNN 模块进行预测可以在某些平台上提高预测速度，但可能会降低预测的准确性
# max_det: 每张图像的最大检测数量
# amp: 是否使用自动混合精度进行预测
# half: 是否使用半精度浮点数进行预测，仅在使用 CUDA 设备时有效，默认是 False，即使用单精度浮点数进行预测, 半精度浮点数可以减少内存使用和加速计算，但可能会降低预测的准确性
# vid_stride: 视频预测时的帧间隔
# save_crop: 是否保存预测结果的裁剪图像
# save_json: 是否保存预测结果的 JSON 文件
# save_frames: 是否保存视频预测的每一帧图像
# save_dir: 预测结果保存的目录



# 读取某文件夹中各级子文件夹中的所有图像文件，并根据原路径依次将预测结果保存到对应的子文件夹中
import os
# r 表示原始字符串，避免路径中的反斜杠被转义
# f 表示格式化字符串，可以在字符串中直接使用变量
def predict_images_in_folder(model, folder_path):
    # files: 当前目录下的文件列表(不包含文件夹)
    # dirs: 当前目录下的文件夹列表(不包含文件)
    # root: 当前目录的路径
    for root, dirs, files in os.walk(folder_path): # 按深度优先遍历文件夹
        # print(f"root: {root}")
        # print(f"dirs: {dirs}")
        # print(f"files: {files}")
        # print(f"Processing folder: {root}, number of files: {len(files)}")
        # for file in files:
        #     print(f"File: {file}")

        if (len(files) == 0):
            continue

        print(f"Processing folder: {root}")
        # root去除初始目录folder_path的部分，得到相对路径
        relative_path = os.path.relpath(root, folder_path)
        print(f"Relative path: {relative_path}")
        save_dir = os.path.join('runs/detect/', relative_path) # 预测结果保存的目录
        model.predict(source=root, save=True, conf=0.25, show=False, save_txt=True, save_conf=False,
                              line_width=3, show_labels=True, show_conf=True,
                              save_dir=save_dir, exist_ok=True, project=save_dir,
                              device='cuda:0' if torch.cuda.is_available() else 'cpu',
                              classes=None, agnostic_nms=False, augment=False, visualize=False,
                              data=True, dnn=False, max_det=1000, amp=False, half=False, vid_stride=1,
                              save_crop=True, save_json=True, save_frames=False)
        # for file in files:
        #     if file.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tiff')):
                # image_path = os.path.join(root, file)
                

        


# main函数，程序入口
def main():
    print("Starting prediction...")
    folder_path = r'E:\StevenWork\UnderwaterGarbageClassification\dataset'
    predict_images_in_folder(model, folder_path)

# 判断当前文件是否被直接运行（而非被导入）
if __name__ == "__main__":
    main()