# UnderwaterGarbageClassification

本项目致力于解决水下垃圾分类问题，提供了一套从数据预处理、模型训练到部署测试的完整工作流。主要使用 **MMYOLO** (基于 MMDet) 实现 **YOLOv8** 模型在水下垃圾数据集上的训练与应用。

---

## 🚀 项目概览
- **核心框架**: PyTorch, MMYOLO, MMDetection
- **模型算法**: YOLOv8 (m/s)
- **主要流程**: 数据清洗 -> 标签格式转换 -> 数据集划分 -> 模型训练 -> 性能评估 -> API 部署
- **主要代码文件简介**:
   - `DataPreprocessing.py`: 使用 YOLO 模型对文件夹中的图片进行批量预测，并将结果保存到本地。
   - `ChangeYoloFormat.py`: 将 YOLO 格式的标注转换为 COCO 格式的 JSON 文件，供 MMYOLO 训练使用。
   - `TrainingSetPartitioning.py`: 将原始图片和标签按比例划分为训练集与验证集，并自动整理目录结构。
   - `models/first_ocean_trash_train.py`: 基于 YOLOv8m 的训练配置文件，读取类别文件并加载预训练权重进行训练。
   - `models/third_ocean_trash_train.py`: 另一个 YOLOv8s 训练配置版本，主要用于不同训练策略和参数组合的对比。
   - `models/ocean_trash_infer.py`: 用于模型推理的配置文件，定义类别信息和检测头参数。
   - `modelEvaluation/ModelAnalyze2.py`: 解析训练日志并绘制学习率与损失曲线。
   - `modelEvaluation/ModelAnalyze3.py`: 解析训练日志中的 AP 和 AR 指标并生成可视化趋势图。
   - `deploy.py`: 基于 FastAPI 封装模型推理接口，提供图片上传后的在线检测服务。

---


## 🛠️ 环境构建 (Conda)

基础准备：安装配置conda环境，可百度相关教程来完成此步骤，这里不做详细介绍

建议使用 Python 3.8+ 版本创建虚拟环境：

```bash
# 创建并激活环境
conda create -n water-trash python=3.8 -y
conda activate water-trash

# 安装 PyTorch (根据你的 CUDA 版本调整，以下为示例) 具体参见下方PyTorch官网 
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# 安装 MMEngine 和 MMDetection，是mmyolo运行的核心环境
pip install -U openmim
mim install mmengine
mim install "mmdet>=3.0.0"

# clone MMYOLO 仓库，后续训练模型需要用到
git clone https://github.com/open-mmlab/mmyolo.git
cd mmyolo
pip install -r requirements/albu.txt
pip install -v -e .
cd ..

# 安装其他依赖
pip install opencv-python matplotlib fastapi uvicorn

# 如需使用到mmcv中图像处理、图像增强的算法，需要安装mmcv
pip install mmcv==2.0.0 -f https://download.openmmlab.com/mmcv/dist/cu118/torch2.0/index.html


```

需要查询Pytorch版，请点击此处：[Pytorch版本匹配](https://pytorch.org/get-started/previous-versions/)
需要查询GPU架构对应的计算能力，请点击此处：[英伟达GPU计算能力查询](https://developer.nvidia.cn/cuda/gpus)
mmcv和Pytorch版本匹配查询，请点击此处：[mmcv版本查询](https://mmcv.readthedocs.io/en/latest/get_started/installation.html)


**PyTorch安装Tips** (针对GPU版本)
> 1. 每个版本的Pytorch 会针对2-3个不同版本的Pytorch的 <br>
>    每个CUDA ToolKit对应的计算能力不同
> 2. 终端输入 nvidia-smi 显示的是当前 NVIDIA 显卡驱动所支持的最高 CUDA
> 3. 安装Pytorch不一定需要安装CUDA ToolKit，但需要注意以下两点
>> 1. 驱动支持的 CUDA 版本 ≥ 框架编译所用的 CUDA 版本
>> 2.  CUDA Toolkit 版本对应的 compute capability 支持范围 和 显卡的 compute capability 是否适配

以下是常见CUDA和计算能力的匹配情况

| 架构代号 | 代表显卡 | 计算能力 | 常见支持的 CUDA 版本范围 |
| --- | --- | --- | --- |
| Pascal | GTX 1080 Ti | 6.1 | CUDA 8.0 到 CUDA 12.x |
| Turing | RTX 20系列 | 7.5 | CUDA 10.0 到 最新版 |
| Ampere | RTX 30系列 | 8.6 | CUDA 11.1 到 最新版 |
| Ada Lovelace | RTX 40系列 | 8.9 | 原生支持 CUDA 11.8+ |
| Blackwell | RTX 50系列 | 12.0 | 原生支持 CUDA 12.4+ |


---

## 📥 模型下载与准备

1. **预训练权重**:
   - 项目中使用了 `yolov8m.pt` 等官方权重作为起点，可以用于测试对比或半自动标注
   - MMYOLO 的权重文件 (如 `yolov8_s_mask-refine...pth`) 会在训练或部署脚本中指定路径加载。<br>
      [下载地址](https://github.com/open-mmlab/mmyolo/tree/main/configs/yolov8)

2. **下载路径**: 确保将下载好的权重放在 `models/` 目录下。目前在models目录中已经保存了两个mmyolo的权重文件
---

## 📂 数据处理流程

初始数据集下载[链接](https://pan.baidu.com/s/136cVzLg7iSVLcFnfhyCMGQ?pwd=k5st) <br>
该数据集为2023-2025年间人工拍摄的水下或岸上垃圾

### 1. 标注数据
- 使用 LabelImg 或 Labelme 等工具进行标注。
- 将标注结果存放在 `dataset/label` 目录下（YOLO 格式 `.txt`）。
- 原始图片存放在 `dataset/originPic` 下。
- 对于同类物品的变化不太多的数据集，可以采用半自动标注的方式，即先标注一部分进行训练，用训练好的模型自动生成剩下部分的标注信息，再手工修改偏差。可用DataPreprocessing.py文件来跑半自动标注流程 <br>

  对于本项目提供的数据集，鉴于数据量不大，建议采用手工标注，

如果不想进行手工标注，这里也提供了部分以及已经标注过的图片信息共使用，点击[此处](https://pan.baidu.com/s/17Q_PfjH-OFVa1VAvP7nGtg?pwd=3i4c)下载


### 2. 分配数据集
使用 `TrainingSetPartitioning.py` 将数据集按比例（默认 9:1）划分为训练集和验证集：
```bash
python TrainingSetPartitioning.py
```
这将在 `dataset/splitData/` 生成平铺后的 `images` 和 `labels`。`images` 和 `labels` 中分别有 `train`, `val` 文件夹对应训练集和验证集


### 3. 转换数据集 (YOLO to COCO)
由于 MMYOLO 通常使用 COCO 格式，需要使用 `ChangeYoloFormat.py` 将 YOLO `.txt` 标签转换为 COCO 格式的 JSON。

若直接按照上述操作执行将分配后的生成到 dataset/splitData/ 文件夹，将标注类型文件classes.txt放置在dataset文件后可直接执行以下命令

```bash
python ChangeYoloFormat.py
```

详细的示例命令及各参数说明如下：

```bash
python ChangeYoloFormat.py \
   --train-labels-dir ./dataset/splitData/labels/train \
   --train-images-dir ./dataset/splitData/images/train \
   --val-labels-dir ./dataset/splitData/labels/val \
   --val-images-dir ./dataset/splitData/images/val \
   --classes-file ./dataset/classes.txt \
   --train-output annotationsCocoTrain.json \
   --val-output annotationsCocoVal.json \
   --exts .jpg .jpeg .png
```

参数说明：

- `--train-labels-dir`: 训练集标签目录（YOLO 格式的 `.txt` 文件），脚本会遍历该目录下的 `.txt` 文件以生成训练集标注。
- `--train-images-dir`: 训练集图片根目录，脚本会**递归搜索**该目录，按图片基名（不含后缀）与标签文件匹配。
- `--val-labels-dir`: 验证集标签目录（YOLO `.txt`），对应验证集的 COCO 输出。
- `--val-images-dir`: 验证集图片根目录（递归搜索），用于查找与标签同名的图片文件。
- `--classes-file`: 每行一个类别名的文件（UTF-8 编码），用于在 COCO 文件中生成 `categories`（若不提供则类别列表为空）。
- `--train-output`: 训练集输出的 COCO JSON 文件路径（例如 `annotationsCocoTrain.json`）。
- `--val-output`: 验证集输出的 COCO JSON 文件路径（例如 `annotationsCocoVal.json`）。
- `--exts`: 可识别的图片扩展名列表，空格分隔（默认示例为 `.jpg .jpeg .png`）。脚本会将扩展名统一为小写后匹配。

脚本行为要点：

- 图片匹配基于文件基名（`basename` 不含后缀）。若在图片目录中找到多个同名图片，会使用第一个匹配项并打印警告。
- `--train-images-dir` 和 `--val-images-dir` 支持嵌套子目录，脚本会递归查找图片文件并生成相对路径写入 COCO 的 `file_name` 字段。
- 若需仅处理单组（非 train/val 分别处理），也可以修改脚本调用或将标签/图片暂时放入对应的 train/val 路径。

示例（最小用法，只生成单个输出文件，可先将所有标签和图片放在同一对路径下）：

```bash
python ChangeYoloFormat.py --train-labels-dir ./labels --train-images-dir ./images --classes-file classes.txt --train-output annotations.json --exts .jpg .png
```



---

## 🏋️ 模型训练

1. **环境检查**

   因为包之间的冲突，建议将目前conda环境中的numpy版本调到2.0.0以下，防止后续训练模型时报错
   ```bash
   pip install "numpy<2.0.0" 
   ```

   再检查一下MMYOLO是否已经装配到本地或服务器的conda环境中
   ```bash
   python -c "import mmyolo; print(mmyolo.__version__)"
   ```



2. **模型结构文件**
   - 该项目提供了两个版本的模型构建文件，存放于models目录中的first_ocean_trash_train.py 和 third_ocean_trash_train.py
   - 两个版本主要是在预训练模型的选择、学习率的迭代方法和batch_size、epoch等参数上有变动
   - 相对来说使用first_ocean_trash_train.py耗显存更多、训练时间更长、精度会高一些，但有过拟合风险
   - 使用third_ocean_trash_train则训练时间较短，且迭代的更加顺滑，但精度会低一些
   - 将模型构建文件放到MMYOLO项目中configs/yolov8文件夹中，标注的自定义类别文件classes.txt也放到同一级目录下

3. **修改配置文件**: 
   
   检查 `models/third_ocean_trash_train.py` 或 `models/first_ocean_trash_train.py` 的如下信息

   1. `data_root` 数据集根目录
   2. `load_from` 预训练模型权重文件路径 (建议先下载好权重文件)


4. **启动训练**:
   使用 MMYOLO 提供的训练工具，确保已经在预先构建好的conda环境后
   在MMYOLO的根目录中执行以下命令：
   
   ```bash
   $env:KMP_DUPLICATE_LIB_OK="TRUE"
   python mmyolo/tools/train.py models/third_ocean_trash_train.py
   ```
   训练日志将保存在 `work_dirs/` 目录下。

   如果运行时有环境问题，可尝试直接安装MMYOLO目录下的requirements.
---

## 📊 模型评估与日志分析

- **评估**: 训练过程中每隔一定 epoch 会自动进行评估（配置文件中 `val_interval` 设置）。
- **分析日志**: 使用 `modelEvaluation/ModelAnalyze2.py` 和 `modelEvaluation/ModelAnalyze3.py` 对日志数据进行可视化 

   ModelAnalyze2 分析的是学习率和损失值的变化情况

   ModelAnalyze3 分析的是精确率AP和召回率AR的变化情况
   
   logs目录中存放的是之前训练过程中的日志数据

   后续日志数据放到此目录中

   ```bash
   python modelEvaluation/ModelAnalyze2.py --file-name xxx.log
   ```
  该脚本会生成 `training_curves.png` 包含学习率和各项损失的变化趋势。

---

## 🧪 测试与推理

### 环境检查
在部署服务的conda环境中执行以下命令
```bash
python -c "from mmyolo.utils import register_all_modules; register_all_modules(); print('MMYOLO 注册成功！')"
```
如果看到 “MMYOLO 注册成功！”，说明你的服务环境已经就绪。

### 模型测试
使用以下命令可以测试模型的检测情况
```bash
python demo/image_demo.py \
    E:/test_images/your_image.jpg \    # 你要测试的图片路径。也可以是文件夹
    configs/yolov8/ocean_trash.py \    # 你训练时用的配置文件。
    work_dirs/ocean_trash/best_coco_bbox_mAP_epoch_XXX.pth \   # 训练生成的权重文件。
    --device cuda:0 \  # 使用显卡进行推理；如果使用cpu推理，改为 --device cpu。
    --out-dir E:/test_results/         # 推理结果（带框的图片）保存的目录。

```

### 脚本推理
使用 `DataPreprocessing.py` (尽管是用于预处理的半自动标注，但包含预测代码) 进行批量图片预测：
```bash
python DataPreprocessing.py
```

### 模型导出
使用以下命令将模型导出为ONNX格式 (尽管是用于预处理的半自动标注，但包含预测代码) 进行批量图片预测：
```bash
python projects/easydeploy/tools/export.py \
    configs/yolov8/ocean_trash_infer.py \
    work_dirs/ocean_trash/best_coco_bbox_mAP_epoch_50.pth \  
    --work-dir work_dirs/onnx_export \
    --img-size 640 640
```
后三个参数分别是模型训练后的权重文件、导出目录和模型输入图像尺寸


### API 部署

使用 `deploy.py` 启动基于 FastAPI 的推理服务。`deploy.py` 支持通过命令行参数或环境变量覆盖模型配置和权重路径。

- 直接使用默认值启动（使用脚本内的默认路径或环境变量）：
```bash
python deploy.py
```

- 使用命令行参数覆盖配置和权重路径：
```bash
python deploy.py \
   --config-path configs/yolov8/ocean_trash_infer.py \
   --checkpoint-path work_dirs/ocean_trash/best_coco_bbox_mAP_epoch_50.pth \
   --device cuda:0 \
   --host 0.0.0.0 \
   --port 8000
```

- 或者通过环境变量配合 `uvicorn` 启动（适合直接导入 `app` 并用 `uvicorn deploy:app` 运行的场景）：
```bash
set CONFIG_PATH=configs/yolov8/ocean_trash_infer.py
set CHECKPOINT_PATH=work_dirs/ocean_trash/best_coco_bbox_mAP_epoch_50.pth
uvicorn deploy:app --host 0.0.0.0 --port 8000
```

参数说明：

- `--config-path`: 模型配置文件路径（默认：`configs/yolov8/ocean_trash_infer.py`）
- `--checkpoint-path`: 模型权重文件路径（默认：`work_dirs/ocean_trash/best_coco_bbox_mAP_epoch_50.pth`）
- `--device`: 推理设备，例如 `cuda:0` 或 `cpu`（默认：`cuda:0`）
- `--host`: 服务绑定地址（默认：`0.0.0.0`）
- `--port`: 服务监听端口（默认：`8000`）

环境变量（优先级低于 CLI 参数，但可在使用 `uvicorn deploy:app` 时生效）：

- `CONFIG_PATH`: 与 `--config-path` 等价
- `CHECKPOINT_PATH`: 与 `--checkpoint-path` 等价


默认运行在 `http://localhost:8000`。可以使用 `curl` 测试：
```bash
curl -X POST "http://localhost:8000/predict" -F "file=@/path/to/trash.jpg"
```

---

## 📁 目录结构说明
- `dataset/`: 存放原始图片、标签及划分后的数据集。
- `models/`: 模型配置文件 (`.py`) 和权重文件 (`.pt`/`.pth`)。
- `logs/`: 训练产生的日志文件。
- `modelEvaluation/`: 性能指标分析脚本。
- `deploy.py`: 后端推理接口实现。
- `ChangeYoloFormat.py`: 格式转换工具。
- `TrainingSetPartitioning.py`: 数据集划分工具。


