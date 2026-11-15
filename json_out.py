import json
import os
import sys

import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("DEEPSEEK_API_KEY", "").strip()
URL = "https://api.deepseek.com/chat/completions"


def build_messages(name, condition, price):
    """把商品信息拼成 messages"""
    system = (
        "你是二手商品文案助手。只输出 JSON，不要解释，不要 markdown 代码块。"
        '格式：{"title":"...","desc":"...","tags":["..."],"price_hint":0}'
    )
    user = f"商品：{name}；成色：{condition}；期望价：{price} 元"
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]


def call_llm(messages, json_mode=True):
    """调接口，返回纯文本"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",     # 通行证：Bearer + 空格 + Key
        "Content-Type": "application/json",       # 我发的是 JSON
    }
    payload = {
        "model": "deepseek-chat",
        "messages": messages,
        "temperature": 0.7,
    }
    if json_mode:                                   # 只有需要 JSON 时才加这个参数
        payload["response_format"] = {"type": "json_object"}

    resp = requests.post(URL, headers=headers, json=payload, timeout=30)

    if resp.status_code != 200:                   # 失败要能看见原因
        print("HTTP", resp.status_code, resp.text[:300])
        return None

    return resp.json()["choices"][0]["message"]["content"]   # 取出文本


def parse_json(text):
    """把模型返回的文本清理成 dict，失败抛异常"""
    if not text:                                  # ① 空值先挡掉
        raise ValueError("模型返回为空")

    cleaned = text.strip()                        # ② 去首尾空白
    cleaned = (
        cleaned.removeprefix("```json")           # ③ 剥掉 ```json
        .removeprefix("```")                      #    剥掉 ```
        .removesuffix("```")                      #    剥掉结尾 ```
        .strip()
    )

    return json.loads(cleaned)                    # ④ 文本 → 字典


def generate(name, condition, price):
    """最多尝试 2 次"""
    for attempt in range(2):                      # ① 最多两次
        try:
            messages = build_messages(name, condition, price)
            raw = call_llm(messages)
            return parse_json(raw)                # ② 成功就直接返回，跳出循环
        except (json.JSONDecodeError, ValueError) as e:
            print(f"[第 {attempt + 1} 次失败] {e}，重试中……")
    return None                                   # ③ 两次都失败


if __name__ == "__main__":
    data = generate("捷安特山地车", "九成新", 800)
    if data:
        print("标题：", data["title"])
        print("描述：", data["desc"])
        print("标签：", data["tags"])
        print("建议价：", data["price_hint"])
    else:
        print("生成失败")

