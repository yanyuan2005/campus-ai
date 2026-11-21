import os

from dotenv import load_dotenv
from fastapi_offline import FastAPIOffline as FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from json_out import build_messages, call_llm, parse_json
from vector_store import search_hybrid, ensure_index 


load_dotenv()

app = FastAPI(title="校园二手交易 AI 服务", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.on_event("startup")
def _prepare_index():
    path = "docx.txt"
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            ensure_index(f.read(), size=400)

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

class AskRequest(BaseModel):
    question: str
    top_k: int = 3


class AskResponse(BaseModel):
    answer: str
    sources: list[str]


@app.post("/ai/ask", response_model=AskResponse)
def ask(req: AskRequest):
    try:
        docs, dists = search_hybrid(req.question, k=req.top_k)

        # 没检索到内容 → 直接兜底，不让模型瞎编
        if not docs:
            return {"answer": "未收录相关问题，请换个问法或联系客服。", "sources": []}

        context = "\n\n".join(f"[{i+1}] {d}" for i, d in enumerate(docs))

        messages = [
            {
                "role": "system",
                "content": (
                    "你是校园二手交易平台的客服。只依据【参考资料】回答问题；"
                    "资料中没有的内容，直接回答“未收录”，不要编造。"
                    "如果参考资料与问题无关，也只回答“未收录”，并且不要标注来源。"
                    "回答简洁，并在末尾用（来源：序号）标注依据。"
                ),
            },
            {
                "role": "user",
                "content": f"【参考资料】\n{context}\n\n【问题】{req.question}",
            },
        ]

        # 改成
        answer = call_llm(messages, json_mode=False) or "未收录相关问题。"
        return {"answer": answer, "sources": [d[:120] for d in docs]}

    except Exception as exc:
        print("[ask 降级]", type(exc).__name__, exc)
        return {"answer": "服务暂时不可用，请稍后重试。", "sources": []}