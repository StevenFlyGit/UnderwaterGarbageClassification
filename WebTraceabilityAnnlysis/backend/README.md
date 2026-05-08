# 海洋垃圾溯源分析后端服务

## 📋 服务介绍

本服务用于对接扣子(Coze)平台的多模态智能体，为前端海洋垃圾识别系统提供AI溯源分析能力。

## 🔧 功能特性

- ✅ 支持图片上传分析
- ✅ 支持多图片批量分析
- ✅ 调用扣子智能体进行多模态分析
- ✅ 自动提取垃圾特征
- ✅ 来源活动概率分析
- ✅ 扩散路径预测
- ✅ 友好的错误处理
- ✅ 完整的日志记录

## 🚀 快速开始

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 配置API Token

编辑 `config.py` 文件，填入您的扣子API Token：

```python
COZE_TOKEN = "your-token-here"
```

### 3. 启动服务

**Windows:**
```bash
.\start.bat
```

**Linux/Mac:**
```bash
chmod +x start.sh
./start.sh
```

### 4. 测试服务

```bash
# 健康检查
curl http://localhost:8080/health

# 提交分析（需要图片文件）
curl -X POST http://localhost:8080/trace \
  -F "file=@test.jpg"
```

## 📡 API接口

### POST /trace

溯源分析接口

**请求参数：**
- `file` (必需): 图片文件，支持JPG、PNG
- `analysis_depth` (可选): 分析深度 - `quick`/`standard`/`deep`
- `source_type` (可选): 来源类型 - `all`/`land`/`marine`
- `time_range` (可选): 时间范围 - `7days`/`30days`/`90days`/`all`
- `confidence_threshold` (可选): 置信度阈值 0-100

**返回格式：**
```json
{
  "status": "success",
  "data": {
    "features": {
      "category": "塑料瓶",
      "material": "高密度聚乙烯(HDPE)",
      "size": "小型",
      "文字": "农夫山泉",
      "特征": ["透明塑料", "圆柱形", "容量约500ml"]
    },
    "source_analysis": {
      "渔业活动": 0.15,
      "旅游活动": 0.45,
      "船舶活动": 0.20,
      "沿海居民": 0.15,
      "工业活动": 0.03,
      "不明来源": 0.02
    },
    "diffusion": {
      "方向": "东南方向",
      "范围": "中等距离（5-20km）",
      "时间线": "30天内可能扩散至近岸海域",
      "高风险区域": ["旅游海滩区域", "近岸渔场"]
    },
    "confidence": 0.85,
    "建议": "建议加强该旅游区域的垃圾回收设施配置"
  },
  "duration": 2.35
}
```

### GET /health

健康检查接口

**返回：**
```json
{
  "status": "healthy",
  "service": "marine-waste-trace-api",
  "timestamp": "2024-01-25T14:30:00"
}
```

## 🔨 前端对接

### 方法一：直接调用本服务

修改前端 `index.html` 中的API地址：

```javascript
const TRACE_API_URL = 'http://localhost:8080/trace';
```

### 方法二：部署到云服务器

1. 将后端代码部署到云服务器
2. 修改前端API地址为服务器地址
3. 配置Nginx反向代理
4. 启用HTTPS（生产环境必需）

## 📁 项目结构

```
backend/
├── trace_api.py       # 主服务文件
├── config.py          # 配置文件
├── requirements.txt   # Python依赖
├── start.bat          # Windows启动脚本
├── start.sh           # Linux/Mac启动脚本
└── README.md          # 说明文档
```

## ⚙️ 配置说明

### 扣子平台配置

1. 在扣子平台创建智能体
2. 配置多模态大模型（推荐通义千问VL或GPT-4V）
3. 编写溯源分析提示词
4. 发布智能体
5. 获取API Token和项目ID

### 提示词配置

编辑 `trace_api.py` 中的 `TRACE_PROMPT_TEMPLATE` 变量，调整分析逻辑和输出格式。

## 🐛 常见问题

### 1. API调用失败
- 检查网络连接
- 确认API Token是否有效
- 检查扣子智能体是否发布

### 2. 超时错误
- 调整 `API_TIMEOUT` 配置
- 减少上传图片数量
- 优化提示词加快分析速度

### 3. CORS跨域问题
- 配置Nginx反向代理
- 或在Flask中启用CORS支持

## 📞 技术支持

如有问题，请检查：
1. 控制台错误日志
2. 网络请求详情
3. 扣子平台智能体状态
