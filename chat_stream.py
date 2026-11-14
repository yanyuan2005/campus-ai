r"""Day 2：流式输出（边生成边打印）

用法（PowerShell）：
    cd D:\code\ai-app
    .\.venv\Scripts\python.exe chat_stream.py

要点：
1. payload 里加 "stream": True
2. 服务端按行返回 SSE：每行形如  data: {...}
3. 最后一行是  data: [DONE]
4. 每块里取 choices[0].delta.content（注意是 delta，不是 message）
"""
import json
import os
import sys
import time

import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
if not api_key.startswith("sk-"):
    print("[错误] .env 里没读到 DEEPSEEK_API_KEY")
    sys.exit(1)

URL = "https://api.deepseek.com/chat/completions"
HEADERS = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
}

question = input("你问点什么（回车用默认）：").strip() or "用三句话介绍什么是 RESTful 接口"

payload = {
    "model": "deepseek-chat",
    "messages": [
        {"role": "system", "content": "你是一个简洁的助手。"},
        {"role": "user", "content": question},
    ],
    "temperature": 0.7,
    "stream": True,          # ← 关键
}

start = time.time()
first_token_at = None
chars = 0

print("\n回答：", end="", flush=True)

try:
    with requests.post(URL, headers=HEADERS, json=payload, stream=True, timeout=60) as resp:
        if resp.status_code != 200:
            print("\n[HTTP 错误]", resp.status_code, resp.text[:300])
            sys.exit(1)

        for raw in resp.iter_lines(decode_unicode=True):
            if not raw:
                continue
            if not raw.startswith("data:"):
                continue
            data_str = raw[5:].strip()
            if data_str == "[DONE]":
                break
            try:
                chunk = json.loads(data_str)
            except json.JSONDecodeError:
                continue

            delta = chunk["choices"][0].get("delta", {})
            piece = delta.get("content") or ""
            if piece:
                if first_token_at is None:
                    first_token_at = time.time() - start
                chars += len(piece)
                print(piece, end="", flush=True)

            finish = chunk["choices"][0].get("finish_reason")
            if finish:
                print(f"\n\n[结束原因] {finish}")

except requests.exceptions.Timeout:
    print("\n[超时] 60 秒未响应")
    sys.exit(1)
except requests.exceptions.RequestException as exc:
    print("\n[网络错误]", exc)
    sys.exit(1)

total = time.time() - start
print(f"[首字延迟] {first_token_at:.2f}s" if first_token_at else "[首字延迟] 未知")
print(f"[总耗时] {total:.2f}s   [字符数] {chars}   [速度] {chars / total:.1f} 字/秒")
