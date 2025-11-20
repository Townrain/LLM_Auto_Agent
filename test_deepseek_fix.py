#!/usr/bin/env python3
"""
测试 DeepSeek API 修复
"""
import os
import json
import requests
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 获取 API Key
api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    print("❌ 未找到 DEEPSEEK_API_KEY 环境变量")
    print("请确保 .env 文件存在并包含 DEEPSEEK_API_KEY=your_api_key")
    exit(1)

print(f"✅ API Key 已加载: {api_key[:10]}...")

# 测试消息格式
messages = [
    {
        "role": "user",
        "content": "你好，请简单回复'测试成功'"
    }
]

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

payload = {
    "model": "deepseek-chat",
    "messages": messages,
    "stream": False
}

print("\n📤 发送测试请求...")
print(f"请求消息格式: {json.dumps(messages, indent=2, ensure_ascii=False)}")

try:
    response = requests.post(
        "https://api.deepseek.com/chat/completions",
        headers=headers,
        json=payload,
        timeout=30
    )
    
    print(f"\n📥 响应状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        print(f"✅ API 测试成功！")
        print(f"🤖 模型回复: {content}")
    else:
        print(f"❌ API 调用失败: {response.status_code}")
        print(f"错误信息: {response.text}")
        
except Exception as e:
    print(f"❌ 请求异常: {str(e)}")