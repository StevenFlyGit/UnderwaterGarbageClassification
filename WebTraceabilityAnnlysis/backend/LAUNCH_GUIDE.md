# 后端服务启动说明

## ⚠️ 当前问题
Python环境配置有问题，Flask模块无法正常导入。请按照以下步骤手动启动服务。

## 🔧 手动启动步骤

### 步骤1：安装Python依赖

打开命令提示符（CMD），执行以下命令：

```cmd
cd d:\File\WJSL\backend
python -m pip install flask requests
```

如果权限不足，尝试：
```cmd
python -m pip install --user flask requests
```

### 步骤2：启动服务

安装成功后，执行：

```cmd
cd d:\File\WJSL\backend
python trace_api.py
```

如果看到以下输出，说明服务启动成功：
```
============================================================
🌊 海洋垃圾溯源分析后端服务
============================================================
API端点: http://localhost:8080/trace
扣子项目ID: 7635556815685730339
============================================================
```

### 步骤3：测试服务

打开浏览器访问：
- 健康检查：http://localhost:8080/health
- API信息：http://localhost:8080/

## 📡 API接口说明

### POST /trace
溯源分析接口

**cURL测试：**
```cmd
curl -X POST http://localhost:8080/trace -F "file=@图片路径\test.jpg"
```

**Python测试：**
```python
import requests

url = 'http://localhost:8080/trace'
files = {'file': open('test.jpg', 'rb')}
response = requests.post(url, files=files)
print(response.json())
```

### GET /health
健康检查

```cmd
curl http://localhost:8080/health
```

## 🔧 备用方案：使用Node.js

如果Python环境无法正常工作，可以使用Node.js作为替代：

```javascript
// 使用Express.js创建后端服务
const express = require('express');
const app = express();
const axios = require('axios');
const FormData = require('form-data');

app.post('/trace', async (req, res) => {
    // 实现与扣子API的对接
});

app.listen(8080);
```

## 📞 常见问题

### 1. "ModuleNotFoundError: No module named 'flask'"
**解决：**
- 确保使用正确的Python命令
- 尝试 `py -3 trace_api.py`
- 检查PATH环境变量

### 2. 端口8080被占用
**解决：**
- 停止占用端口的程序
- 或修改 `trace_api.py` 中的端口号

### 3. 扣子API调用失败
**检查：**
- API Token是否正确
- 项目ID是否正确
- 网络连接是否正常
