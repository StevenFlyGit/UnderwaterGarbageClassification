"""
海洋垃圾溯源分析后端服务
对接扣子平台多模态智能体
"""

from flask import Flask, request, jsonify
import requests
import json
import base64
import time
from datetime import datetime
import os

app = Flask(__name__)

# 扣子API配置
COZE_API_URL = "https://4p9tqrwrxp.coze.site/stream_run"
COZE_TOKEN = "eyJhbGciOiJSUzI1NiIsImtpZCI6IjBkYzU5M2IxLTNmYWUtNGM2NC1hYTJhLTc3MzgzMjQ0MzM2MSJ9.eyJpc3MiOiJodHRwczovL2FwaS5jb3plLmNuIiwiYXVkIjpbIlVJSXRRTWlOdlA3RGVoN2k2b3ZtcWY1dk9rd1ZYWHZJIl0sImV4cCI6ODIxMDI2Njg3Njc5OSwiaWF0IjoxNzc3Nzk1NDEwLCJzdWIiOiJzcGlmZmU6Ly9hcGkuY296ZS5jbi93b3JrbG9hZF9pZGVudGl0eS9pZDo3NjM1NTcwMjE1MTA2OTA0MDY0Iiwic3JjIjoiaW5ib3VuZF9hdXRoX2FjY2Vzc190b2tlbl9pZDo3NjM1NTczMTQ3NDc5MDQ4MjQzIn0.eNf4_caqoS0fXITQdJ8wjChNqYtAWbfxJKwpAU7VeFgCsdy3ezj_eTJxaKsbBmpBTBhjBf04HymeRVzis0gFhe_UYDuhJwdHX1cDHFyx4kdN8cEwcmYaKzuByviP4QbOxlO8NZlS4GWiBdPfzSqC_ChLvRGkIO5HWzO3RPXGmDLfzbNUcpuV0njxmd3XHs1zP78XStpbbOhD0D8i7oekKbxsBn7X-JWeILR-3NtrDqt0od11HS3WfIVvK6jW72bXeiNqfcTuS3HI50JOshpL2IW6aUPwuxYrrw5tA0ibAHzkqdnnKPyHsXdNsq87h5IwjnOA30l_lPx4Crm0xs_mxQ"
PROJECT_ID = 7635556815685730339

# 分析提示词模板
TRACE_PROMPT_TEMPLATE = """你是一个专业的海洋垃圾溯源分析专家。请仔细分析这张图片中的垃圾物品，并提供详细的溯源分析报告。

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
}
"""


@app.route('/trace', methods=['POST'])
def trace_analysis():
    """
    溯源分析接口
    接收图片文件，调用扣子智能体进行分析
    """
    start_time = time.time()

    try:
        # 检查是否有文件
        if 'file' not in request.files and 'files' not in request.files:
            return jsonify({
                'status': 'error',
                'message': '请上传图片文件'
            }), 400

        # 获取文件
        files = request.files.getlist('files') or [request.files['file']]
        file = files[0]

        if not file:
            return jsonify({
                'status': 'error',
                'message': '未找到文件'
            }), 400

        # 读取图片并转为base64
        image_bytes = file.read()
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')

        # 获取分析参数
        analysis_depth = request.form.get('analysis_depth', 'standard')
        source_type = request.form.get('source_type', 'all')
        time_range = request.form.get('time_range', '30days')
        confidence_threshold = float(request.form.get('confidence_threshold', 60)) / 100

        # 生成session_id
        session_id = f"BKrpdrOyq6aArwZYA0OnA{int(time.time())}"

        # 构造扣子API请求
        payload = {
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
            "session_id": session_id,
            "project_id": PROJECT_ID
        }

        # 调用扣子API
        headers = {
            "Authorization": f"Bearer {COZE_TOKEN}",
            "Content-Type": "application/json"
        }

        response = requests.post(
            COZE_API_URL,
            headers=headers,
            json=payload,
            timeout=120
        )

        if response.status_code != 200:
            return jsonify({
                'status': 'error',
                'message': f'扣子API调用失败: {response.status_code}',
                'details': response.text
            }), 500

        result = response.json()
        duration = time.time() - start_time

        # 解析扣子返回的结果
        analysis_result = parse_coze_response(result)

        if analysis_result:
            # 应用置信度过滤
            if analysis_result.get('confidence', 0) < confidence_threshold:
                return jsonify({
                    'status': 'success',
                    'data': analysis_result,
                    'message': '分析完成但置信度较低',
                    'duration': round(duration, 2)
                })
            else:
                return jsonify({
                    'status': 'success',
                    'data': analysis_result,
                    'duration': round(duration, 2)
                })
        else:
            return jsonify({
                'status': 'success',
                'data': generate_mock_result(),
                'message': '使用模拟数据（扣子返回格式解析中）',
                'duration': round(duration, 2)
            })

    except requests.Timeout:
        return jsonify({
            'status': 'error',
            'message': '请求超时，请稍后重试'
        }), 504

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'分析失败: {str(e)}'
        }), 500


def parse_coze_response(response):
    """
    解析扣子API返回的结果
    """
    try:
        # 扣子返回格式可能包含多个字段，需要根据实际情况调整
        if isinstance(response, dict):
            # 尝试提取消息内容
            messages = response.get('messages', [])
            for msg in messages:
                if msg.get('role') == 'assistant':
                    content = msg.get('content', '')
                    # 尝试解析JSON
                    return extract_json_from_text(content)

        # 如果无法解析，返回None触发模拟数据
        return None
    except Exception as e:
        print(f"解析扣子响应失败: {e}")
        return None


def extract_json_from_text(text):
    """
    从文本中提取JSON
    """
    try:
        # 尝试直接解析
        return json.loads(text)
    except:
        # 尝试查找JSON块
        import re
        json_match = re.search(r'\{[\s\S]*\}', text)
        if json_match:
            try:
                return json.loads(json_match.group())
            except:
                pass
        return None


def generate_mock_result():
    """
    生成模拟分析结果（用于测试）
    """
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
    }


@app.route('/health', methods=['GET'])
def health_check():
    """
    健康检查接口
    """
    return jsonify({
        'status': 'healthy',
        'service': 'marine-waste-trace-api',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/', methods=['GET'])
def index():
    """
    首页
    """
    return jsonify({
        'service': '海洋垃圾溯源分析API',
        'version': '1.0.0',
        'endpoints': {
            'POST /trace': '提交图片进行溯源分析',
            'GET /health': '健康检查',
            'GET /': 'API信息'
        }
    })


if __name__ == '__main__':
    print("=" * 60)
    print("🌊 海洋垃圾溯源分析后端服务")
    print("=" * 60)
    print(f"API端点: http://localhost:8080/trace")
    print(f"扣子项目ID: {PROJECT_ID}")
    print("=" * 60)

    # 启动服务
    app.run(host='0.0.0.0', port=8080, debug=True)
