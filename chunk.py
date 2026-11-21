import sys

sys.stdout.reconfigure(encoding="utf-8")

def split_text(text, size=500, overlap=50):
    chunks = []
    start = 0
    while start < len(text):
        chunks.append(text[start:start + size])
        start += size - overlap
    return chunks


if __name__ == "__main__":
    with open("docx.txt", encoding="utf-8") as f:      # 注意：你的文件名是 docx.txt
        text = f.read()

    print(f"原文 {len(text)} 字")
    chunks = split_text(text)
    print(f"共 {len(chunks)} 块")

    for i, c in enumerate(chunks[:3]):
        print(f"[{i}] 长度 {len(c)}：{c[:30]}…")

    if len(chunks) > 1:
        print("重叠验证：", chunks[0][-50:] == chunks[1][:50])
def split_by_sections(text: str, max_len: int = 400) -> list[str]:
    """优先按 ## 小节切块：每节语义完整，比固定长度切更好检索。"""
    parts, cur = [], []
    for line in text.splitlines():
        if line.startswith("## ") and cur:
            parts.append("\n".join(cur).strip())
            cur = [line]
        else:
            cur.append(line)
    if cur:
        parts.append("\n".join(cur).strip())

    chunks: list[str] = []
    for p in parts:
        p = p.strip()
        if not p:
            continue
        if len(p) <= max_len:
            chunks.append(p)
        else:
            chunks.extend(split_text(p, size=max_len // 2, overlap=30))
    return chunks
