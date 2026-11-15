import sys

import chromadb

from embed import embed

sys.stdout.reconfigure(encoding="utf-8")

client = chromadb.PersistentClient(path="./chroma_db")
col = client.get_or_create_collection("campus_docs")


def build_index(chunks: list[str]):
    """把切好的块和它们的向量一起存进去"""
    if col.count() > 0:
        print(f"库里已有 {col.count()} 条，跳过")
        return

    vecs = embed(chunks)
    col.add(
        documents=chunks,
        ids=[f"c{i}" for i in range(len(chunks))],
        embeddings=vecs,
    )
    print(f"已存入 {len(chunks)} 条")


def search(query: str, k: int = 3):
    """检索最相关的 k 块，返回 (文档列表, 距离列表)"""
    qv = embed([query])[0]
    res = col.query(query_embeddings=[qv], n_results=k)
    return res["documents"][0], res["distances"][0]

def ensure_index(text: str, size: int = 500, overlap: int = 50):
    """库里没数据就自动灌，云端启动时调用"""
    if col.count() > 0:
        return
    from chunk import split_text
    chunks = split_text(text, size=size, overlap=overlap)
    build_index(chunks)
    print(f"[索引] 已自动构建 {len(chunks)} 块")

if __name__ == "__main__":
    from chunk import split_text

    with open("docx.txt", encoding="utf-8") as f:
        text = f.read()

    chunks = split_text(text)
    build_index(chunks)

    docs, dists = search("退款规则是什么")
    for i, (d, s) in enumerate(zip(docs, dists)):
        print(f"[{i}] 距离 {s:.4f}：{d[:60]}…")