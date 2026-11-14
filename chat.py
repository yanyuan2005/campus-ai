r"""Day 1：最简大模型调用（DeepSeek）

用法（PowerShell）：
    cd D:\code\ai-app
    .\.venv\Scripts\python.exe chat.py
"""
import os
import sys

import requests
from dotenv import load_dotenv

load_dotenv()  # 读取同目录下的 .env

api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()  #os.getenv("名字", "") 的意思是：找得到就返回它的值，找不到就返回空字符串（第二个参数是默认值）
if not api_key or not api_key.startswith("sk-"):
    print("[错误] 没读到 Key。请检查 D:\\code\\ai-app\\.env 里是否为：")
    print("       DEEPSEEK_API_KEY=sk-你的key")
    sys.exit(1)    #sys.exit() = 立刻停止整个程序，括号里的 1 是“退出码”：0 表示正常结束，非 0 表示出错了。

print("Key 读取成功：", api_key[:6] + "****" + api_key[-4:])

URL = "https://api.deepseek.com/chat/completions" #调用api接口大模型，URL：发给谁（地址）
HEADERS = {
    "Authorization": f"Bearer {api_key}",   #我的身份和格式（带 Key 的通行证）
    "Content-Type": "application/json",
}

question = input("你问点什么（直接回车用默认问题）：").strip() or "用一句话解释什么是 API"

payload = {
    "model": "deepseek-chat",
    "messages": [
        {"role": "system", "content": "你是一个简洁的助手，回答不超过 40 字。"},
        {"role": "user", "content": question},
    ],
    "temperature": 0.7,
}

print("\n正在请求……")
try:
    resp = requests.post(URL, headers=HEADERS, json=payload, timeout=30) #json=payload：我要说的话（Python 字典 → 自动转成 JSON）
except requests.exceptions.Timeout:
    print("[超时] 30 秒没响应，检查网络")
    sys.exit(1)
except requests.exceptions.RequestException as exc:
    print("[网络错误]", exc)
    sys.exit(1)

print("状态码：", resp.status_code)

if resp.status_code != 200:
    print("出错内容：", resp.text[:500])    
    sys.exit(1)

data = resp.json()
print("\n回答：", data["choices"][0]["message"]["content"])
print("用量：", data["usage"])
