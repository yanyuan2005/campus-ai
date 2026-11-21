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

# ---------- 混合检索：向量相似度 + 关键词覆盖率 ----------
def _bigrams(s: str) -> set[str]:
    s = "".join(ch for ch in s if ch.strip())
    return {s[i : i + 2] for i in range(len(s) - 1)}


def search_hybrid(query: str, k: int = 3, min_score: float = 0.32):
    """返回 (文档列表, 得分列表)。得分低于 min_score 视为未命中，返回空。

    为什么加关键词：中文短问句与长段落做纯向量相似度时，命中率不稳定；
    这里把「向量余弦相似度」与「查询词二元组覆盖率」按 55/45 加权，
    既保留语义检索，又能兜住「运费」「信用分」这类关键词型问题。
    """
    total = col.count()
    if total == 0:
        return [], []

    qv = embed([query])[0]
    res = col.query(query_embeddings=[qv], n_results=total)
    docs = res["documents"][0]
    dists = res["distances"][0]

    qb = _bigrams(query)
    scored = []
    for doc, dist in zip(docs, dists):
        cosine = max(0.0, 1 - dist / 2)          # 归一化向量的平方 L2 距离 → 余弦
        cover = len(qb & _bigrams(doc)) / max(1, len(qb))
        score = 0.55 * cosine + 0.45 * cover
        scored.append((score, doc))

    scored.sort(key=lambda x: -x[0])
    if not scored or scored[0][0] < min_score:
        return [], []

    top = scored[:k]
    return [d for _, d in top], [round(s, 4) for s, _ in top]
