import os
import sys

import requests
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding="utf-8")
load_dotenv()

ZHIPU_URL = "https://open.bigmodel.cn/api/paas/v4/embeddings"


def embed(texts: list[str]) -> list[list[float]]:
    """把一批文本转成向量，返回 [向量1, 向量2, ...]"""
    key = os.getenv("ZHIPU_API_KEY", "").strip()
    if not key:
        print("[错误] .env 里没有 ZHIPU_API_KEY")
        sys.exit(1)

    resp = requests.post(
        ZHIPU_URL,
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
        json={"model": "embedding-3", "input": texts},
        timeout=30,
    )

    if resp.status_code != 200:
        print("HTTP", resp.status_code, resp.text[:300])
        return []

    data = resp.json()["data"]
    # 按 index 排序，保证顺序和输入一致
    data.sort(key=lambda x: x.get("index", 0))

    return [item["embedding"] for item in data]


if __name__ == "__main__":
    vecs = embed(["校园二手交易平台支持七天无理由退款"])
    print("条数：", len(vecs))
    print("维度：", len(vecs[0]) if vecs else 0)
    print("前 5 个数：", vecs[0][:5] if vecs else None)