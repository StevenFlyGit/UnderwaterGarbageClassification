import os
import cv2
import numpy as np
from fastapi import FastAPI, File, UploadFile
import uvicorn

from mmengine.config import Config
from mmdet.apis import init_detector, inference_detector

import torch
torch.set_num_threads(2) # 云服务器上使用，本地调试可注释
# 限制 PyTorch 使用的线程数，避免在 CPU 上运行时过度占用资源导致系统卡顿。根据你的 CPU 核心数和实际需求调整这个数字

# 异常问题记录
# 这个 KeyError: 'YOLODetector is not in the mmdet::model registry' 错误是 MMLab 系列框架中非常经典的问题。
# 这个错误的根本原因是 MMYOLO 模块没有正确注册到 MMDectection 的模型注册表中，导致在加载配置文件时找不到 YOLODetector 这个类。


# 解决你之前遇到的 OpenMP 冲突问题
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

# --- 配置区 ---
# 请确保路径指向你目前表现最好的模型权重文件和正确的配置文件
CONFIG_PATH = 'configs/yolov8/ocean_trash.py'
CHECKPOINT_PATH = 'work_dirs/ocean_trash/best_coco_bbox_mAP_epoch_50.pth'
DEVICE = 'cuda:0' # 如果服务器没显卡则改为 'cpu'

# # 1. 关键一步：注册 MMYOLO 模块，解决 YOLODetector 找不到的问题
# from mmyolo.utils import register_all_modules
# # init_default_scope=True 确保使用 mmyolo 默认作用域，避免落到 mmdet::model registry
# register_all_modules(init_default_scope=True)

# # 导入 mmdet 的推理器
# from mmdet.apis import DetInferencer



# # 初始化推理器 (DetInferencer 是 MMYOLO 最简单的调用方式)
# inferencer = DetInferencer(model=CONFIG_PATH, weights=CHECKPOINT_PATH, device=DEVICE)


# 2. 暴力修复法：手动构建配置并强制注入 mmyolo 库
cfg = Config.fromfile(CONFIG_PATH)
# 在配置中强制添加自定义导入，确保 YOLODetector 被加载
cfg.custom_imports = dict(imports=['mmyolo.models'], allow_failed_imports=False)

print("正在初始化模型...")
# 使用更底层的 init_detector 代替 DetInferencer，这样更稳定
model = init_detector(cfg, CHECKPOINT_PATH, device=DEVICE)
print("模型初始化成功！")

# 提取出类别列表
class_names = model.dataset_meta.get('classes', [])

app = FastAPI(title="海洋垃圾识别系统 API")

# 如何用curl命令测试文件上传接口：
# curl -X POST "http://localhost:8000/predict" -H "accept: application/json" -H "Content-Type: multipart/form-data" -F "file=@/path/to/your/image.jpg"
# @符号后面跟的是你要上传的图片的路径，记得替换成你自己的图片路径。这个命令会向 /predict 端点发送一个 POST 请求，并上传指定的图片文件。
# windos下的路径需要使用双反斜杠或者正斜杠，例如：
# curl -X POST "http://localhost:8000/predict" -H "accept: application/json" -H "Content-Type: multipart/form-data" -F "file=@E:\\path\\to\\your\\image.jpg"

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    print(f"收到文件: {file.filename}")
    # 1. 读取上传的图片
    contents = await file.read() # await 关键字确保我们正确处理异步文件读取，避免阻塞事件循环，尤其是在处理大文件时。
    # file.read() 返回的是字节流，是fastAPI中请求读取文件的方式，我们需要将其转换为 OpenCV 可处理的格式，首先转换为 numpy 数组，然后解码成图像。
    nparr = np.frombuffer(contents, np.uint8) # 将字节流转换为 numpy 数组
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR) # 解码成图像，cv2.IMREAD_COLOR 确保以彩色模式读取
    
    # 2. 模型推理
    # out_dir 设置为空，我们直接在内存中处理结果
    results = inference_detector(model, img) 

    # 3. 解析结果
    # inference_detector 返回的是 DetDataSample（或列表），其预测信息在 .pred_instances
    det_sample = results[0] if isinstance(results, (list, tuple)) else results

    pred_instances = getattr(det_sample, 'pred_instances', None) # 安全地获取 pred_instances，避免属性错误
    # pred_instances 通常包含 bboxes/scores/labels
    # boxes/scores/labels 分别对应检测框坐标、置信度分数和类别标签，我们将它们转换为 numpy 数组以便后续处理。
    # 由于不同版本的 MMDetection/MMYOLO 可能返回不同类型的数据结构，我们需要编写一个兼容性函数来安全地提取这些信息。
    output = []
    if pred_instances is None:
        return {"status": "success", "data": output}

    # 安全地提取 boxes/scores/labels，兼容 Tensor/ndarray/InstanceData
    def to_numpy(x):
        try:
            return x.numpy()
        except Exception:
            try:
                import torch
                if isinstance(x, torch.Tensor):
                    return x.detach().cpu().numpy()
            except Exception:
                pass
            return np.array(x)

    try:
        bboxes = to_numpy(pred_instances.bboxes)
        scores = to_numpy(pred_instances.scores)
        labels = to_numpy(pred_instances.labels)
    except Exception:
        # 兜底：如果没有这些属性或结构不同，返回空列表
        return {"status": "success", "data": output}

    # 只返回置信度大于 0.3 的目标
    keep = scores > 0.3
    for score, label, bbox in zip(scores[keep], labels[keep], bboxes[keep]):

        # 通过索引直接获取名称
        label_id = int(label)
        label_name = class_names[label_id] if label_id < len(class_names) else "Unknown"

        output.append({
            "class_id": label_id,
            "class_name": label_name, # 返回类别对应的名称
            "confidence": round(float(score), 4),
            "bbox": [round(float(x), 2) for x in bbox]
        })
            
    return {"status": "success", "data": output}

if __name__ == "__main__":
    # 启动服务，监听 8000 端口
    uvicorn.run(app, host="0.0.0.0", port=8000)