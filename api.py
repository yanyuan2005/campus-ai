import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi_offline import FastAPIOffline as FastAPI
from pydantic import BaseModel
from json_out import build_messages, call_llm, parse_json

load_dotenv()

app = FastAPI(title="校园二手交易 AI 服务", version="1.0")


class DescribeRequest(BaseModel):
    name: str
    condition: str = "未填写"
    price: int = 0


class DescribeResponse(BaseModel):
    title: str
    desc: str
    tags: list[str]
    price_hint: int
    source: str


def fallback(req: DescribeRequest) -> dict:
    return {
        "title": f"{req.name} {req.condition}"[:20],
        "desc": f"{req.name}，{req.condition}，价格 {req.price} 元，同城自提，诚心可小刀。",
        "tags": ["二手", "校园"],
        "price_hint": req.price,
        "source": "fallback",
    }


@app.post("/ai/describe", response_model=DescribeResponse)
def describe(req: DescribeRequest):
    try:
        messages = build_messages(req.name, req.condition, req.price)
        raw = call_llm(messages)
        data = parse_json(raw)

        if not data:
            return fallback(req)

        data["source"] = "ai"
        return data

    except Exception as exc:
        print("[降级]", type(exc).__name__, exc)
        return fallback(req)


@app.get("/health")
def health():
    return {"status": "ok"}