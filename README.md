# 校园二手交易 AI 服务

基于 FastAPI + 大模型的商品文案生成与 RAG 问答服务，作为「校园二手交易小程序」的 AI 能力后端。

## 在线演示

https://campus-ai-lljm.onrender.com/docs

> Render 免费实例会休眠，首次访问约需 50 秒冷启动。

## 接口

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | `/ai/describe` | 商品文案生成（结构化 JSON + 失败降级） |
| POST | `/ai/ask` | RAG 问答（向量检索 + 引用来源 + 防幻觉） |
| GET | `/health` | 健康检查 |

## 技术栈

Python 3.13 · FastAPI · Pydantic · DeepSeek API · 智谱 embedding · Chroma · requests

## 关键实现

- **结构化输出**：`response_format=json_object` + Pydantic 模型，保证返回可直接解析
- **失败降级**：模型超时/报错时回退模板文案，接口永不 500；响应 `source` 字段区分 `ai` / `fallback`
- **RAG 检索**：文档按 500 字切块（重叠 50）→ embedding 向量化（2048 维）→ 存入 Chroma →
  检索 Top-3 拼入 Prompt，答案标注来源
- **防幻觉**：检索距离超过阈值判为未收录；提示词约束“只依据资料回答”，不相关时不标注来源
- **Key 安全**：Key 存于环境变量/`.env`，不入库；前端不直接调用大模型

## 运行

```bash
pip install -r requirements.txt
cp .env.example .env    # 填入 DEEPSEEK_API_KEY / ZHIPU_API_KEY
uvicorn api:app --reload --port 8010
