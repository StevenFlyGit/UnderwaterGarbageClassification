"""
配置文件
请勿将本文件提交到版本控制系统
"""

# 扣子API配置
COZE_API_URL = "https://4p9tqrwrxp.coze.site/stream_run"
COZE_TOKEN = "YOUR_COZE_TOKEN_HERE"
PROJECT_ID = 7635556815685730339

# 服务配置
HOST = "0.0.0.0"
PORT = 8080
DEBUG = True

# 文件上传配置
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'mp4', 'mov'}

# 分析配置
DEFAULT_ANALYSIS_DEPTH = "standard"
DEFAULT_SOURCE_TYPE = "all"
DEFAULT_TIME_RANGE = "30days"
DEFAULT_CONFIDENCE_THRESHOLD = 60
API_TIMEOUT = 120  # 秒
