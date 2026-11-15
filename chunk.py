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




















