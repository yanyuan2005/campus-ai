r"""实验 A：只保留 `if not api_key:` 判断

目的：证明「只判断有没有值」挡不住「格式错误的 Key」——
      假的 key 会通过检查，一直跑到服务器，被 401 拒绝。

用法：
    cd D:\code\ai-app
    .\.venv\Scripts\python.exe test_a.py

注意：跑之前把 .env 里的 Key 改成随手写的假值（例如 ab123）
"""
import os
import sys

import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()

print("=== 实验 A：只判断「有没有」 ===")
print("读到的 Key：", repr(api_key))

# ----------------- 关键差异就在这一行 -----------------
if not api_key:                      # 只判断空值
    print("[拦截] 没读到 Key")
    sys.exit(1)
# ------------------------------------------------------

print("[通过] 检查认为 Key 没问题，准备发请求……\n")

resp = requests.post(
    "https://api.deepseek.com/chat/completions",
    headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    },
    json={
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": "你好"}],
    },
    timeout=30,
)

print("状态码：", resp.status_code)
print("返回内容：", resp.text[:300])

if resp.status_code == 401:
    print("\n[结论] 假 Key 通过了「有没有」的检查，但被服务器拒绝（401）。")
    print("       所以还需要判断它「像不像」Key —— 这正是加 startswith('sk-') 的原因。")
