"""
海洋垃圾溯源分析 - Python代理服务器（简化版）
"""

import json
import re
import urllib.request
import urllib.error
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.error import HTTPError

# 扣子API配置
COZE_API_URL = "https://4p9tqrwrxp.coze.site/stream_run"
COZE_TOKEN = "eyJhbGciOiJSUzI1NiIsImtpZCI6IjBkYzU5M2IxLTNmYWUtNGM2NC1hYTJhLTc3MzgzMjQ0MzM2MSJ9.eyJpc3MiOiJodHRwczovL2FwaS5jb3plLmNuIiwiYXVkIjpbIlVJSXRRTWlOdlA3RGVoN2k2b3ZtcWY1dk9rd1ZYWHZJIl0sImV4cCI6ODIxMDI2Njg3Njc5OSwiaWF0IjoxNzc3Nzk3NTAyLCJzdWIiOiJzcGlmZmU6Ly9hcGkuY296ZS5jbi93b3JrbG9hZF9pZGVudGl0eS9pZDo3NjM1NTcwMjE1MTA2OTA0MDY0Iiwic3JjIjoiaW5ib3VuZF9hdXRoX2FjY2Vzc190b2tlbl9pZDo3NjM1NTgyMTMyNDgzNTIyNjAyIn0.YhrF7AvMyR6-F1gc74MpO3Gjmyg5w5HI8_VfflUt0ytuQhUa7Yo8IrQwCLryjdAYdyDBRHQW26WSv1DZnU_BuT9SXgsYL-SYhFdq8d2KBizCmBm_3Y-4GTQal4ksJwfbQa3osUfJzFJp0fst_QFC-WuKtEw8ds4Id1AyyWVI9HUAXP8MRGs_Pnj9UlrJkpYh_6DM1jo_E0VmdVNAOHdw45D7BwN1YtxlAoVbG_KMY2W7nncaF8_HebL-M_P-RA_bxk65r39P-Jb5dzMb6kXJmLTufwFJ70qCP0l_Eq70nIeXoEwEtIexmya2eTUKzlR2utaY8cqlLzS9BXME3Es7zA"
PROJECT_ID = "7635556815685730339"

PORT = 8080

def get_prompt():
    return """你是一个专业的海洋垃圾溯源分析专家。请分析图片中的垃圾并提供详细报告。

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
}"""

def parse_sse_stream(sse_text):
    """从SSE流中提取所有answer片段并拼接"""
    answer_parts = []
    
    # 分割每个SSE事件（用空行分割）
    events = sse_text.split('\n\n')
    
    for event in events:
        if not event.strip():
            continue
            
        # 查找 data: {"type": "answer", ...}
        # 或者 data: {"type": "message_end", ...}
        if '"type"' in event and '"answer"' in event:
            # 提取JSON部分
            json_match = re.search(r'\{[^{}]*"answer"\s*:\s*"([^"]*)"[^{}]*\}', event)
            if json_match:
                # 提取answer字段的值
                answer_text = json_match.group(1)
                answer_parts.append(answer_text)
    
    return ''.join(answer_parts)

def extract_json_from_text(text):
    """从文本中提取JSON"""
    if not text:
        return None
    
    # 清理文本
    text = text.strip()
    
    # 如果文本以 { 开头，尝试直接解析
    if text.startswith('{'):
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
    
    # 查找JSON对象
    json_match = re.search(r'\{[\s\S]*\}', text)
    if json_match:
        json_str = json_match.group(0)
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"JSON解析错误: {e}")
            print(f"尝试解析的文本: {json_str[:200]}")
    
    return None

class ProxyHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()

    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {'status': 'healthy', 'service': 'marine-waste-trace-proxy'}
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path != '/trace':
            self.send_response(404)
            self.end_headers()
            return

        try:
            # 读取请求数据
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            
            session_id = f"proxy-{hash(str(body))}"
            
            payload = {
                "content": {
                    "query": {
                        "prompt": [{
                            "type": "text",
                            "content": {
                                "text": get_prompt()
                            }
                        }]
                    }
                },
                "type": "query",
                "session_id": session_id,
                "project_id": PROJECT_ID
            }
            
            headers = {
                "Authorization": "Bearer " + COZE_TOKEN,
                "Content-Type": "application/json",
                "Accept": "text/event-stream"
            }
            
            print("调用扣子API...")
            
            # 发送请求到扣子
            req = urllib.request.Request(
                COZE_API_URL,
                data=json.dumps(payload).encode('utf-8'),
                headers=headers,
                method='POST'
            )
            
            try:
                with urllib.request.urlopen(req, timeout=120) as response:
                    sse_text = response.read().decode('utf-8')
            except HTTPError as e:
                error_body = e.read().decode('utf-8')
                print(f"扣子API错误 {e.code}: {error_body}")
                self.send_response(e.code)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'status': 'error',
                    'message': f'扣子API错误: {e.code}'
                }).encode())
                return
            
            print(f"收到SSE数据长度: {len(sse_text)}")
            print(f"SSE数据前200字符: {sse_text[:200]}")
            
            # 解析SSE
            answer_text = parse_sse_stream(sse_text)
            print(f"提取的answer文本长度: {len(answer_text)}")
            print(f"answer文本: {answer_text[:200]}")
            
            # 提取JSON
            result_data = extract_json_from_text(answer_text)
            
            # 发送响应
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            if result_data:
                print("成功解析JSON!")
                self.wfile.write(json.dumps({
                    'status': 'success',
                    'data': result_data
                }).encode())
            else:
                print("无法解析JSON，返回错误信息")
                self.wfile.write(json.dumps({
                    'status': 'error',
                    'message': '无法解析JSON',
                    'raw_answer': answer_text[:500] if answer_text else '无数据'
                }).encode())
                
        except Exception as e:
            print(f"服务器错误: {e}")
            import traceback
            traceback.print_exc()
            
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({
                'status': 'error',
                'message': str(e)
            }).encode())

    def log_message(self, format, *args):
        print(f"[{self.address_string()}] {format % args}")

def main():
    server = HTTPServer(('0.0.0.0', PORT), ProxyHandler)
    print("=" * 60)
    print("海洋垃圾溯源分析代理服务器")
    print("=" * 60)
    print(f"端口: {PORT}")
    print(f"地址: http://localhost:{PORT}/trace")
    print("按 Ctrl+C 停止")
    print("=" * 60)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n服务器已停止")
        server.server_close()

if __name__ == "__main__":
    main()
