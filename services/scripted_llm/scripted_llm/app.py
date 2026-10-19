"""A deterministic, OpenAI-compatible chat model.

It sits behind the LLM gateway exactly like a real provider, so budgets, rate limits
and spend logs are exercised in CI without an API key. Responses are fixed strings;
token usage is a word count so cost attribution is non-zero and predictable.
"""

import time
import uuid

from fastapi import FastAPI
from pydantic import BaseModel

MODEL_ID = "scripted"

app = FastAPI(title="scripted-llm")


class Message(BaseModel):
    role: str
    content: str | None = None


class ChatRequest(BaseModel):
    model: str
    messages: list[Message]


def count_tokens(text: str) -> int:
    return max(1, len(text.split()))


def reply_for(messages: list[Message]) -> str:
    last_user = next((m.content or "" for m in reversed(messages) if m.role == "user"), "")
    return f"[scripted] Received {count_tokens(last_user)} words. No real model was called."


@app.get("/healthz")
def healthz() -> dict:
    return {"status": "ok"}


@app.get("/v1/models")
def models() -> dict:
    return {"object": "list", "data": [{"id": MODEL_ID, "object": "model", "owned_by": "local"}]}


@app.post("/v1/chat/completions")
def chat_completions(request: ChatRequest) -> dict:
    content = reply_for(request.messages)
    prompt_tokens = sum(count_tokens(m.content or "") for m in request.messages)
    completion_tokens = count_tokens(content)
    return {
        "id": f"chatcmpl-{uuid.uuid4().hex}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": MODEL_ID,
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": content},
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
        },
    }
