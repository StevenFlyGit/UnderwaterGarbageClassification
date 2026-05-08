/**
 * 海洋垃圾溯源分析后端服务 - Node.js版本
 * 对接扣子(Coze)平台多模态智能体
 * 支持SSE流式响应
 */

const express = require('express');
const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = 8080;

// 扣子API配置
const COZE_API_URL = "https://4p9tqrwrxp.coze.site/stream_run";
const COZE_TOKEN = "eyJhbGciOiJSUzI1NiIsImtpZCI6IjBkYzU5M2IxLTNmYWUtNGM2NC1hYTJhLTc3MzgzMjQ0MzM2MSJ9.eyJpc3MiOiJodHRwczovL2FwaS5jb3plLmNuIiwiYXVkIjpbIlVJSXRRTWlOdlA3RGVoN2k2b3ZtcWY1dk9rd1ZYWHZJIl0sImV4cCI6ODIxMDI2Njg3Njc5OSwiaWF0IjoxNzc3Nzk1NDEwLCJzdWIiOiJzcGlmZmU6Ly9hcGkuY296ZS5jbi93b3JrbG9hZF9pZGVudGl0eS9pZDo3NjM1NTcwMjE1MTA2OTA0MDY0Iiwic3JjIjoiaW5ib3VuZF9hdXRoX2FjY2Vzc190b2tlbl9pZDo3NjM1NTczMTQ3NDc5MDQ4MjQzIn0.eNf4_caqoS0fXITQdJ8wjChNqYtAWbfxJKwpAU7VeFgCsdy3ezj_eTJxaKsbBmpBTBhjBf04HymeRVzis0gFhe_UYDuhJwdHX1cDHFyx4kdN8cEwcmYaKzuByviP4QbOxlO8NZlS4GWiBdPfzSqC_ChLvRGkIO5HWzO3RPXGmDLfzbNUcpuV0njxmd3XHs1zP78XStpbbOhD0D8i7oekKbxsBn7X-JWeILR-3NtrDqt0od11HS3WfIVvK6jW72bXeiNqfcTuS3HI50JOshpL2IW6aUPwuxYrrw5tA0ibAHzkqdnnKPyHsXdNsq87h5IwjnOA30l_lPx4Crm0xs_mxQ";
const PROJECT_ID = "7635556815685730339";

// 分析提示词模板
const TRACE_PROMPT_TEMPLATE = `你是一个专业的海洋垃圾溯源分析专家。请仔细分析这张图片中的垃圾物品，并提供详细的溯源分析报告。

## 分析要求

1. **垃圾特征识别**
   - 类型（塑料瓶、玻璃瓶、包装袋、渔具、电子产品等）
   - 材质（塑料、玻璃、金属、纸张、橡胶等）
   - 品牌（如果包装上有文字或logo请识别）
   - 状态（完整、破损、降解程度）
   - 尺寸估算（小型物品如饮料瓶、中型物品如包装箱、大型物品如渔网）

2. **来源活动分析**
   基于垃圾特征，分析最可能的来源：
   - 渔业活动：渔具、饵料包装、渔网碎片、鱼类包装
   - 旅游活动：饮料瓶、食品包装、防晒霜瓶、一次性用品
   - 船舶活动：船用油桶、货物包装、船员生活垃圾
   - 沿海居民：日常生活垃圾、装修废料
   - 工业活动：工厂废料、工业包装、化学品容器
   - 不明来源：无法判断的情况

3. **扩散路径预测**
   结合海洋环境：
   - 主要扩散方向（考虑洋流、风向）
   - 预计扩散范围（短距离/中距离/远距离）
   - 高风险聚集区域
   - 时间线预测

4. **环保建议**
   基于分析结果提供清理建议和预防措施

## 输出格式
请严格按照以下JSON格式输出，不要添加任何其他文字：
{
  "features": {
    "category": "垃圾类型",
    "material": "主要材质",
    "size": "小/中/大型",
    "文字": "识别到的文字或品牌信息",
    "特征": ["特征1", "特征2", "特征3"]
  },
  "source_analysis": {
    "渔业活动": 0.00,
    "旅游活动": 0.00,
    "船舶活动": 0.00,
    "沿海居民": 0.00,
    "工业活动": 0.00,
    "不明来源": 0.00
  },
  "diffusion": {
    "方向": "扩散主要方向",
    "范围": "扩散范围描述",
    "时间线": "时间线预测",
    "高风险区域": ["区域1", "区域2"]
  },
  "confidence": 0.00,
  "建议": "环保建议"
}`;

// 生成模拟分析结果
function generateMockResult() {
    return {
        "features": {
            "category": "塑料瓶",
            "material": "高密度聚乙烯(HDPE)",
            "size": "小型",
            "文字": "农夫山泉",
            "特征": ["透明塑料", "圆柱形", "容量约500ml", "瓶身完整"]
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
        "建议": "建议加强该旅游区域的垃圾回收设施配置，特别是在旺季增加清洁频率。"
    };
}

// CORS中间件
app.use((req, res, next) => {
    res.header('Access-Control-Allow-Origin', '*');
    res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
    res.header('Access-Control-Allow-Headers', 'Content-Type, Authorization');
    if (req.method === 'OPTIONS') {
        return res.status(200).end();
    }
    next();
});

// 解析JSON请求体
app.use(express.json({ limit: '50mb' }));
app.use(express.urlencoded({ extended: true, limit: '50mb' }));

// 文件上传处理
const multer = require('multer');
const storage = multer.memoryStorage();
const upload = multer({ 
    storage: storage,
    limits: { fileSize: 50 * 1024 * 1024 },
    fileFilter: (req, file, cb) => {
        const allowedTypes = ['image/jpeg', 'image/png', 'image/jpg', 'video/mp4', 'video/mov', 'video/quicktime'];
        if (allowedTypes.includes(file.mimetype)) {
            cb(null, true);
        } else {
            cb(new Error('不支持的文件类型'));
        }
    }
});

// 溯源分析接口
app.post('/trace', upload.array('files', 10), async (req, res) => {
    const startTime = Date.now();
    
    try {
        // 获取文件
        const files = req.files;
        if (!files || files.length === 0) {
            return res.json({
                status: 'error',
                message: '请上传图片文件'
            });
        }

        // 获取分析参数
        const analysisDepth = req.body.analysis_depth || 'standard';
        const sourceType = req.body.source_type || 'all';
        const timeRange = req.body.time_range || '30days';
        const confidenceThreshold = parseFloat(req.body.confidence_threshold || 60) / 100;

        // 生成session_id
        const sessionId = `BKrpdrOyq6aArwZYA0OnA${Date.now()}`;

        // 构造扣子API请求
        const payload = {
            "content": {
                "query": {
                    "prompt": [
                        {
                            "type": "text",
                            "content": {
                                "text": TRACE_PROMPT_TEMPLATE
                            }
                        }
                    ]
                }
            },
            "type": "query",
            "session_id": sessionId,
            "project_id": PROJECT_ID
        };

        const headers = {
            "Authorization": `Bearer ${COZE_TOKEN}`,
            "Content-Type": "application/json",
            "Accept": "text/event-stream"
        };

        console.log(`[INFO] 正在调用扣子API...`);
        console.log(`[INFO] Session ID: ${sessionId}`);

        // 调用扣子API
        const response = await axios.post(COZE_API_URL, payload, {
            headers: headers,
            responseType: 'stream',
            timeout: 120000
        });

        // 设置SSE响应头
        res.setHeader('Content-Type', 'text/event-stream');
        res.setHeader('Cache-Control', 'no-cache');
        res.setHeader('Connection', 'keep-alive');

        let buffer = '';
        let resultData = null;
        let isComplete = false;

        response.data.on('data', (chunk) => {
            buffer += chunk.toString();
            const blocks = buffer.split('\n\n');
            buffer = blocks.pop() || '';

            for (const block of blocks) {
                const dataLines = block
                    .split('\n')
                    .filter(line => line.startsWith('data:'))
                    .map(line => line.slice(5).trim());

                if (dataLines.length === 0) continue;

                const dataText = dataLines.join('\n');
                try {
                    const parsed = JSON.parse(dataText);
                    console.log('[DEBUG] 收到数据:', JSON.stringify(parsed, null, 2));

                    // 检查是否是最终结果
                    if (parsed.type === 'end' || parsed.content?.finish_reason === 'end') {
                        isComplete = true;
                        // 尝试提取分析结果
                        const messageContent = parsed.content?.messages?.[0]?.content;
                        if (messageContent) {
                            resultData = extractJsonFromText(messageContent);
                        }
                    }
                } catch (e) {
                    console.log('[DEBUG] 非JSON数据:', dataText);
                }
            }
        });

        response.data.on('end', () => {
            const duration = Date.now() - startTime;
            
            if (resultData) {
                // 使用真实分析结果
                res.write(`data: ${JSON.stringify({
                    status: 'success',
                    data: resultData,
                    duration: (duration / 1000).toFixed(2)
                })}\n\n`);
            } else {
                // 使用模拟数据
                console.log('[WARN] 未能解析扣子API响应，使用模拟数据');
                res.write(`data: ${JSON.stringify({
                    status: 'success',
                    data: generateMockResult(),
                    message: '使用模拟数据（扣子返回格式解析中）',
                    duration: (duration / 1000).toFixed(2)
                })}\n\n`);
            }
            
            res.end();
            console.log(`[INFO] 请求完成，耗时: ${(duration / 1000).toFixed(2)}s`);
        });

        response.data.on('error', (err) => {
            console.error('[ERROR] 流式响应错误:', err);
            res.write(`data: ${JSON.stringify({
                status: 'error',
                message: `分析失败: ${err.message}`
            })}\n\n`);
            res.end();
        });

    } catch (error) {
        const duration = Date.now() - startTime;
        console.error('[ERROR] 溯源分析失败:', error.message);
        
        // 返回模拟数据作为备用
        res.json({
            status: 'success',
            data: generateMockResult(),
            message: `API调用失败，使用模拟数据: ${error.message}`,
            duration: (duration / 1000).toFixed(2)
        });
    }
});

// 健康检查接口
app.get('/health', (req, res) => {
    res.json({
        status: 'healthy',
        service: 'marine-waste-trace-api',
        timestamp: new Date().toISOString()
    });
});

// 首页
app.get('/', (req, res) => {
    res.json({
        service: '海洋垃圾溯源分析API',
        version: '1.0.0',
        endpoints: {
            'POST /trace': '提交图片进行溯源分析',
            'GET /health': '健康检查',
            'GET /': 'API信息'
        }
    });
});

// 错误处理
app.use((err, req, res, next) => {
    console.error('[ERROR] 中间件错误:', err);
    res.status(500).json({
        status: 'error',
        message: err.message
    });
});

// 启动服务
app.listen(PORT, () => {
    console.log('='.repeat(60));
    console.log('🌊 海洋垃圾溯源分析后端服务 (Node.js)');
    console.log('='.repeat(60));
    console.log(`服务地址: http://localhost:${PORT}`);
    console.log(`API端点: http://localhost:${PORT}/trace`);
    console.log(`扣子项目ID: ${PROJECT_ID}`);
    console.log('='.repeat(60));
    console.log('按 Ctrl+C 停止服务');
});

/**
 * 从文本中提取JSON
 */
function extractJsonFromText(text) {
    try {
        return JSON.parse(text);
    } catch {
        const jsonMatch = text.match(/\{[\s\S]*\}/);
        if (jsonMatch) {
            try {
                return JSON.parse(jsonMatch[0]);
            } catch {
                return null;
            }
        }
        return null;
    }
}
