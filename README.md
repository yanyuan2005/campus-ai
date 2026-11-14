# 校园二手交易 AI 服务

基于 FastAPI + 大模型的商品文案生成服务，作为「校园二手交易小程序」的 AI 能力后端。

## 功能

- `POST /ai/describe`：输入商品名、成色、价格，返回结构化的标题 / 描述 / 标签 / 建议售价
- `GET /health`：健康检查

## 技术栈

Python 3.13 · FastAPI · Pydantic · DeepSeek API · requests

## 关键实现

- **结构化输出**：`response_format=json_object` + Pydantic 模型，保证返回可直接解析
- **失败降级**：模型超时/报错时回退模板文案，接口永不 500；响应 `source` 字段区分 `ai` / `fallback`
- **Key 安全**：Key 存于 `.env` 不入库，前端不直接调用大模型（避免泄露）

## 运行

```bash
pip install -r requirements.txt
cp .env.example .env    # 填入 DEEPSEEK_API_KEY
uvicorn api:app --reload --port 8010
