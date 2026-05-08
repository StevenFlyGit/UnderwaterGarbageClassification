/**
 * 海洋垃圾溯源分析 - Node.js代理服务器
 * 解决前端CORS跨域问题
 * 解析SSE流并返回简单JSON
 */

const http = require('http');
const https = require('https');
const { URL } = require('url');

const PORT = 8080;

// 扣子API配置
const COZE_API_URL = 'https://4p9tqrwrxp.coze.site/stream_run';
const COZE_TOKEN = 'eyJhbGciOiJSUzI1NiIsImtpZCI6IjBkYzU5M2IxLTNmYWUtNGM2NC1hYTJhLTc3MzgzMjQ0MzM2MSJ9.eyJpc3MiOiJodHRwczovL2FwaS5jb3plLmNuIiwiYXVkIjpbIlVJSXRRTWlOdlA3RGVoN2k2b3ZtcWY1dk9rd1ZYWHZJIl0sImV4cCI6ODIxMDI2Njg3Njc5OSwiaWF0IjoxNzc3Nzk3NTAyLCJzdWIiOiJzcGlmZmU6Ly9hcGkuY296ZS5jbi93b3JrbG9hZF9pZGVudGl0eS9pZDo3NjM1NTcwMjE1MTA2OTA0MDY0Iiwic3JjIjoiaW5ib3VuZF9hdXRoX2FjY2Vzc190b2tlbl9pZDo3NjM1NTgyMTMyNDgzNTIyNjAyIn0.YhrF7AvMyR6-F1gc74MpO3Gjmyg5w5HI8_VfflUt0ytuQhUa7Yo8IrQwCLryjdAYdyDBRHQW26WSv1DZnU_BuT9SXgsYL-SYhFdq8d2KBizCmBm_3Y-4GTQal4ksJwfbQa3osUfJzFJp0fst_QFC-WuKtEw8ds4Id1AyyWVI9HUAXP8MRGs_Pnj9UlrJkpYh_6DM1jo_E0VmdVNAOHdw45D7BwN1YtxlAoVbG_KMY2W7nncaF8_HebL-M_P-RA_bxk65r39P-Jb5dzMb6kXJmLTufwFJ70qCP0l_Eq70nIeXoEwEtIexmya2eTUKzlR2utaY8cqlLzS9BXME3Es7zA';
const PROJECT_ID = '7635556815685730339';

function getPrompt() {
    return `你是一个专业的海洋垃圾溯源分析专家。请分析图片中的垃圾并提供详细报告。

## 分析要求
1. **垃圾特征识别**
   - 类型（塑料瓶、玻璃瓶、包装袋、渔具等）
   - 材质（塑料、玻璃、金属、纸张等）
   - 品牌（如果有文字或logo）
   - 状态（完整、破损、降解程度）
   - 尺寸估算（小型/中型/大型）

2. **来源活动分析**
   分析来源概率：渔业活动、旅游活动、船舶活动、沿海居民、工业活动、不明来源

3. **扩散路径预测**
   - 主要扩散方向
   - 预计扩散范围
   - 高风险聚集区域
   - 时间线预测

## 输出格式
请严格按照JSON格式输出：
{
  "features": {
    "category": "垃圾类型",
    "material": "材质",
    "size": "小/中/大型",
    "文字": "识别到的文字",
    "特征": ["特征1", "特征2"]
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
    "方向": "扩散方向",
    "范围": "扩散范围",
    "时间线": "时间线",
    "高风险区域": ["区域1", "区域2"]
  },
  "confidence": 0.85,
  "建议": "环保建议"
}`;
}

// 解析SSE流，提取answer数据
function parseSSE(data) {
    const result = { answer: '' };

    // 分割每个事件（用空行分割）
    const events = data.split(/\n\n/);

    for (const event of events) {
        const lines = event.split('\n');

        let eventType = '';
        let eventData = '';

        for (const line of lines) {
            if (line.startsWith('event:')) {
                eventType = line.slice(6).trim();
            } else if (line.startsWith('data:')) {
                eventData = line.slice(5).trim();
            }
        }

        // 只处理answer类型的事件
        if (eventType === 'message' || eventType === '') {
            if (eventData) {
                try {
                    const parsed = JSON.parse(eventData);

                    // 提取answer内容
                    if (parsed.content && parsed.content.answer) {
                        result.answer += parsed.content.answer;
                    }

                    // 如果有完整的消息结束，检查是否有最终结果
                    if (parsed.type === 'message_end' && parsed.content && parsed.content.message_end) {
                        result.done = true;
                    }
                } catch (e) {
                    // JSON解析失败，忽略
                }
            }
        }
    }

    return result;
}

// 从answer字符串中提取JSON
function extractJson(answerStr) {
    // 尝试直接解析
    try {
        return JSON.parse(answerStr);
    } catch (e) {}

    // 尝试从字符串中提取JSON
    const jsonMatch = answerStr.match(/\{[\s\S]*\}/);
    if (jsonMatch) {
        try {
            return JSON.parse(jsonMatch[0]);
        } catch (e) {}
    }

    return null;
}

const server = http.createServer(async (req, res) => {
    // CORS处理
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'POST, GET, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

    // 预检请求
    if (req.method === 'OPTIONS') {
        res.writeHead(200);
        res.end();
        return;
    }

    // 健康检查
    if (req.method === 'GET' && req.url === '/health') {
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({
            status: 'healthy',
            service: 'marine-waste-trace-proxy'
        }));
        return;
    }

    // 溯源分析接口
    if (req.method === 'POST' && req.url === '/trace') {
        let body = '';
        req.on('data', (chunk) => {
            body += chunk.toString();
        });

        req.on('end', async () => {
            try {
                const sessionId = 'proxy-session-' + Date.now();

                const payload = {
                    content: {
                        query: {
                            prompt: [{
                                type: 'text',
                                content: {
                                    text: getPrompt()
                                }
                            }]
                        }
                    },
                    type: 'query',
                    session_id: sessionId,
                    project_id: PROJECT_ID
                };

                const options = {
                    method: 'POST',
                    headers: {
                        'Authorization': 'Bearer ' + COZE_TOKEN,
                        'Content-Type': 'application/json',
                        'Accept': 'text/event-stream'
                    },
                    timeout: 120000
                };

                // 调用扣子API
                const cozeResponse = await new Promise((resolve, reject) => {
                    const cozeReq = https.request(COZE_API_URL, options, (response) => {
                        resolve(response);
                    });
                    cozeReq.on('error', reject);
                    cozeReq.setTimeout(120000, () => {
                        cozeReq.destroy();
                        reject(new Error('Timeout'));
                    });
                    cozeReq.write(JSON.stringify(payload));
                    cozeReq.end();
                });

                // 收集SSE数据
                let sseData = '';
                for await (const chunk of cozeResponse) {
                    sseData += chunk.toString();
                }

                console.log('收到SSE数据长度:', sseData.length);

                // 解析SSE
                const parsed = parseSSE(sseData);
                console.log('提取的answer长度:', parsed.answer.length);
                console.log('提取的answer前100字符:', parsed.answer.substring(0, 100));

                // 提取JSON
                const jsonResult = extractJson(parsed.answer);

                if (jsonResult) {
                    // 返回解析后的JSON
                    res.writeHead(200, { 'Content-Type': 'application/json' });
                    res.end(JSON.stringify({
                        status: 'success',
                        data: jsonResult
                    }));
                } else {
                    // 无法解析，返回原始answer用于调试
                    res.writeHead(200, { 'Content-Type': 'application/json' });
                    res.end(JSON.stringify({
                        status: 'error',
                        message: '无法解析JSON',
                        answer: parsed.answer.substring(0, 500)
                    }));
                }

            } catch (error) {
                console.error('Error:', error);
                res.writeHead(500, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({
                    status: 'error',
                    message: error.message
                }));
            }
        });

        return;
    }

    // 404
    res.writeHead(404);
    res.end();
});

server.listen(PORT, () => {
    console.log('===== Proxy Server Started =====');
    console.log('Port:', PORT);
    console.log('API Endpoint: http://localhost:' + PORT + '/trace');
    console.log('Press Ctrl+C to stop');
    console.log('===============================');
});
