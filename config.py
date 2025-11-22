"""
配置管理模块
集中管理所有配置项和环境变量
"""

import os
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# ============================================================
# API 配置
# ============================================================

API_BASE_URL = os.getenv('API_BASE_URL')
API_ENDPOINT = os.getenv('API_ENDPOINT', '/api/v1/customers')
API_TOKEN = os.getenv('API_TOKEN')

# 验证必需的配置
if not API_BASE_URL:
    raise ValueError("❌ 缺少 API_BASE_URL 配置，请检查 .env 文件")
if not API_TOKEN:
    raise ValueError("❌ 缺少 API_TOKEN 配置，请检查 .env 文件")

# ============================================================
# S3 配置
# ============================================================

S3_BUCKET = os.getenv('S3_BUCKET')
S3_PREFIX = os.getenv('S3_PREFIX', 'raw/customers')

if not S3_BUCKET:
    raise ValueError("❌ 缺少 S3_BUCKET 配置，请检查 .env 文件")

# ============================================================
# 重试和速率限制配置
# ============================================================

MAX_RETRIES = int(os.getenv('MAX_RETRIES', '5'))
INITIAL_BACKOFF = float(os.getenv('INITIAL_BACKOFF', '1'))
RECORDS_PER_PAGE = int(os.getenv('RECORDS_PER_PAGE', '1000'))

# ============================================================
# 其他配置
# ============================================================

REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', '30'))  # 请求超时（秒）
INTER_PAGE_DELAY = float(os.getenv('INTER_PAGE_DELAY', '0.5'))  # 页面间延迟（秒）

# 打印配置（用于调试，不显示敏感信息）
def print_config():
    """打印当前配置（隐藏敏感信息）"""
    print("\n📋 当前配置:")
    print(f"  API URL: {API_BASE_URL}")
    print(f"  API Token: {'*' * 20}...{API_TOKEN[-4:] if API_TOKEN else 'NOT SET'}")
    print(f"  S3 Bucket: {S3_BUCKET}")
    print(f"  S3 Prefix: {S3_PREFIX}")
    print(f"  Max Retries: {MAX_RETRIES}")
    print(f"  Records per Page: {RECORDS_PER_PAGE}")
    print()