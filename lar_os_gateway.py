"""
LAR-OS Unified AI Gateway (Antigravity-First / Dual-Protocol Proxy)
Author: Gia Bao Huynh (Jun) / LAR-OS
Role: Safe, non-destructive bridge presenting OpenAI & Anthropic compatible API endpoints.
Connects Antigravity IDE, WorkBuddy AI, and Claude Code CLI directly into Google Gemini,
the Quad-Browser AI Consortium (Perplexity, Copilot, Gemini, ChatGPT), and Free Cloud Providers.
Port: 18797 (OpenAI Base: http://127.0.0.1:18797/v1 | Anthropic Base: http://127.0.0.1:18797)
"""

import os
import sys
import json
import time
import asyncio
import urllib.request
from typing import Optional, List, Dict, Any, AsyncGenerator
from pathlib import Path

if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8")

from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

SCRATCH = Path(r"C:\Users\nswcl\.gemini\antigravity-ide\scratch")
sys.path.insert(0, str(SCRATCH))

# Try importing local bridges if available
try:
    from opera_chatgpt_operator import operate_chatgpt_on_opera
except Exception:
    operate_chatgpt_on_opera = None

try:
    from edge_copilot_bridge import query_edge_copilot
except Exception:
    query_edge_copilot = None

try:
    from comet_agent import perform_search_and_extract as query_comet
except Exception:
    query_comet = None

try:
    from chrome_gemini_bridge import query_chrome_gemini
except Exception:
    query_chrome_gemini = None

try:
    from quad_browser_ai_consortium import dispatch_quad_ai_search
except Exception:
    dispatch_quad_ai_search = None

CONFIG_PATH = SCRATCH / "gateway_config.json"
DEFAULT_CONFIG = {
    "gateway": {"port": 18797, "auth_token": "lar-os-master"},
    "providers": {
        "gemini": {"default_model": "gemini-2.5-flash"},
        "openrouter": {"base_url": "https://openrouter.ai/api/v1"},
        "nvidia_nim": {"base_url": "https://integrate.api.nvidia.com/v1"}
    }
}

def get_config():
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return DEFAULT_CONFIG

app = FastAPI(title="LAR-OS Unified AI Gateway", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODELS_REGISTRY = [
    {"id": "gemini-2.5-flash", "object": "model", "created": 1700000000, "owned_by": "google", "description": "Google Gemini 2.5 Flash (1M tokens context, fast reasoning)"},
    {"id": "gemini-2.0-flash", "object": "model", "created": 1700000000, "owned_by": "google", "description": "Google Gemini 2.0 Flash (Multimodal & code generation)"},
    {"id": "deepseek-r1-quad", "object": "model", "created": 1700000000, "owned_by": "lar-os-consortium", "description": "LAR-OS Quad-Browser Consensus (Perplexity + Copilot + Gemini + ChatGPT)"},
    {"id": "chatgpt-4o-opera", "object": "model", "created": 1700000000, "owned_by": "openai-opera", "description": "OpenAI ChatGPT via Opera Neon CDP (Port 9225)"},
    {"id": "perplexity-comet", "object": "model", "created": 1700000000, "owned_by": "perplexity", "description": "Perplexity Live Search via Comet CDP (Port 9222)"},
    {"id": "copilot-edge", "object": "model", "created": 1700000000, "owned_by": "microsoft", "description": "Microsoft Copilot GPT-4o via Edge CDP (Port 9223)"},
    {"id": "claude-3.5-sonnet", "object": "model", "created": 1700000000, "owned_by": "anthropic", "description": "Anthropic Claude 3.5 Sonnet (via NIM or proxy)"},
    {"id": "llama-3.3-70b-free", "object": "model", "created": 1700000000, "owned_by": "meta-openrouter", "description": "Meta Llama 3.3 70B Instruct (Free Tier)"}
]

@app.get("/")
@app.get("/health")
async def health_check():
    cfg = get_config()
    return {
        "status": "ONLINE",
        "service": "LAR-OS Unified AI Gateway",
        "architecture": "Non-destructive Dual-Protocol Proxy",
        "compatible_clients": [
            "Antigravity IDE (OpenAI-compatible Add Model)",
            "Tencent WorkBuddy AI (OpenAI-compatible Add Model)",
            "Claude Code CLI ($env:ANTHROPIC_BASE_URL)",
            "Curl / Python OpenAI SDK"
        ],
        "models_count": len(MODELS_REGISTRY),
        "timestamp": time.time()
    }

@app.get("/v1/models")
@app.get("/models")
async def list_models():
    return {"object": "list", "data": MODELS_REGISTRY}

async def generate_response_text(model: str, messages: List[Dict[str, Any]]) -> str:
    # Extract last user prompt
    prompt = ""
    for m in reversed(messages):
        if m.get("role") == "user":
            content = m.get("content", "")
            if isinstance(content, list):
                prompt = " ".join([c.get("text", "") for c in content if isinstance(c, dict) and "text" in c])
            else:
                prompt = str(content)
            break
            
    if not prompt:
        prompt = "Hello from LAR-OS Gateway"

    # Route based on model ID
    model_lower = model.lower()
    
    # 1. Quad-Browser Consensus
    if "quad" in model_lower and dispatch_quad_ai_search:
        res = await dispatch_quad_ai_search(prompt)
        return f"[LAR-OS Quad-Browser Consensus Result]\n\n{json.dumps(res, indent=2, ensure_ascii=False)}"
        
    # 2. Opera Neon ChatGPT
    if "opera" in model_lower or "chatgpt" in model_lower:
        if operate_chatgpt_on_opera:
            await operate_chatgpt_on_opera(prompt)
            return f"Prompt successfully dispatched to ChatGPT on Opera Neon: '{prompt[:80]}...'. Check Opera Neon GUI (Port 9225) for live response."
            
    # 3. Perplexity Comet
    if "perplexity" in model_lower or "comet" in model_lower:
        if query_comet:
            res = await query_comet(prompt)
            return f"[Perplexity Comet Live Search Result]:\n{res}"
            
    # 4. Edge Copilot
    if "copilot" in model_lower or "edge" in model_lower:
        if query_edge_copilot:
            res = await query_edge_copilot(prompt)
            return f"[Microsoft Copilot Result]:\n{res}"

    # 5. Default: Google Gemini via multi-account key pool (or Chrome CDP fallback)
    keys_pool = []
    keys_file = SCRATCH / "gateway_keys.json"
    if keys_file.exists():
        try:
            with open(keys_file, "r", encoding="utf-8") as kf:
                kd = json.load(kf)
                for item in kd.get("api_keys", []):
                    k = item.get("key", "").strip()
                    if k and item.get("status") == "ACTIVE":
                        keys_pool.append({"key": k, "account": item.get("account", "unknown")})
        except Exception:
            pass
            
    # Include env fallback
    env_k = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if env_k and not any(x["key"] == env_k for x in keys_pool):
        keys_pool.append({"key": env_k, "account": "ENV_DEFAULT"})

    global _round_robin_counter
    if "_round_robin_counter" not in globals():
        _round_robin_counter = 0

    if keys_pool:
        # True Round-Robin Load Balancing across active keys
        target_model = "gemini-3.5-flash-lite" if ("flash" in model or "2.5" in model) else model
        n_keys = len(keys_pool)
        start_idx = _round_robin_counter % n_keys
        _round_robin_counter += 1

        ordered_pool = keys_pool[start_idx:] + keys_pool[:start_idx]
        for key_entry in ordered_pool:
            try:
                def _do_request(k, m, p):
                    import urllib.request
                    import json
                    u = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={k}"
                    d = json.dumps({"contents": [{"parts": [{"text": p}]}], "generationConfig": {"maxOutputTokens": 300}}).encode("utf-8")
                    req = urllib.request.Request(u, data=d, headers={"Content-Type": "application/json"}, method="POST")
                    with urllib.request.urlopen(req, timeout=10) as r:
                        if r.status == 200:
                            data = json.loads(r.read().decode("utf-8"))
                            cand = data.get("candidates", [{}])[0]
                            parts = cand.get("content", {}).get("parts", [])
                            if parts:
                                return parts[0].get("text", "")
                    return None

                res_text = await asyncio.to_thread(_do_request, key_entry["key"], target_model, prompt)
                if res_text:
                    print(f"[Gateway Router] Request successfully routed & fulfilled by account: {key_entry['account']} (Model: {target_model})")
                    return res_text
            except Exception as e:
                print(f"[Gateway Router] Key error for {key_entry['account']}: {e}. Rotating to next account...")
                continue

@app.post("/v1/chat/completions")
@app.post("/chat/completions")
async def chat_completions(request: Request):
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")
        
    model = body.get("model", "gemini-2.5-flash")
    messages = body.get("messages", [])
    stream = body.get("stream", False)
    req_id = f"chatcmpl-{int(time.time() * 1000)}"
    created = int(time.time())
    
    full_text = await generate_response_text(model, messages)
    
    if not stream:
        return {
            "id": req_id,
            "object": "chat.completion",
            "created": created,
            "model": model,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": full_text
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": len(str(messages)) // 4,
                "completion_tokens": len(full_text) // 4,
                "total_tokens": (len(str(messages)) + len(full_text)) // 4
            }
        }
        
    # Streaming response
    async def sse_generator() -> AsyncGenerator[str, None]:
        # Split full_text into chunks to simulate high-speed streaming
        words = full_text.split(" ")
        for i, word in enumerate(words):
            chunk = word + (" " if i < len(words) - 1 else "")
            payload = {
                "id": req_id,
                "object": "chat.completion.chunk",
                "created": created,
                "model": model,
                "choices": [
                    {
                        "index": 0,
                        "delta": {"content": chunk},
                        "finish_reason": None
                    }
                ]
            }
            yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"
            await asyncio.sleep(0.02)
            
        final_payload = {
            "id": req_id,
            "object": "chat.completion.chunk",
            "created": created,
            "model": model,
            "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}]
        }
        yield f"data: {json.dumps(final_payload, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"
        
    return StreamingResponse(sse_generator(), media_type="text/event-stream")

@app.post("/v1/messages")
@app.post("/messages")
async def anthropic_messages(request: Request):
    """Anthropic Messages API Compatibility endpoint for Claude Code CLI."""
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")
        
    model = body.get("model", "claude-3-5-sonnet-20241022")
    messages = body.get("messages", [])
    stream = body.get("stream", False)
    msg_id = f"msg_{int(time.time() * 1000)}"
    
    full_text = await generate_response_text(model, messages)
    
    if not stream:
        return {
            "id": msg_id,
            "type": "message",
            "role": "assistant",
            "model": model,
            "content": [
                {
                    "type": "text",
                    "text": full_text
                }
            ],
            "stop_reason": "end_turn",
            "stop_sequence": None,
            "usage": {
                "input_tokens": len(str(messages)) // 4,
                "output_tokens": len(full_text) // 4
            }
        }
        
    # Anthropic SSE streaming format
    async def anthropic_sse_generator():
        yield f"event: message_start\ndata: {json.dumps({'type': 'message_start', 'message': {'id': msg_id, 'type': 'message', 'role': 'assistant', 'model': model, 'content': [], 'usage': {'input_tokens': len(str(messages)) // 4, 'output_tokens': 1}}})}\n\n"
        yield f"event: content_block_start\ndata: {json.dumps({'type': 'content_block_start', 'index': 0, 'content_block': {'type': 'text', 'text': ''}})}\n\n"
        
        words = full_text.split(" ")
        for i, word in enumerate(words):
            chunk = word + (" " if i < len(words) - 1 else "")
            delta_data = {
                "type": "content_block_delta",
                "index": 0,
                "delta": {"type": "text_delta", "text": chunk}
            }
            yield f"event: content_block_delta\ndata: {json.dumps(delta_data, ensure_ascii=False)}\n\n"
            await asyncio.sleep(0.02)
            
        yield f"event: content_block_stop\ndata: {json.dumps({'type': 'content_block_stop', 'index': 0})}\n\n"
        yield f"event: message_delta\ndata: {json.dumps({'type': 'message_delta', 'delta': {'stop_reason': 'end_turn', 'stop_sequence': None}, 'usage': {'output_tokens': len(full_text) // 4}})}\n\n"
        yield f"event: message_stop\ndata: {json.dumps({'type': 'message_stop'})}\n\n"
        
    return StreamingResponse(anthropic_sse_generator(), media_type="text/event-stream")

def run():
    cfg = get_config()
    port = cfg.get("gateway", {}).get("port", 18797)
    host = cfg.get("gateway", {}).get("host", "127.0.0.1")
    print("=" * 85)
    print(f"🚀 LAR-OS UNIFIED AI GATEWAY LAUNCHING ON http://{host}:{port} 🚀")
    print(f"OpenAI Endpoint:     http://{host}:{port}/v1/chat/completions")
    print(f"Anthropic Endpoint:  http://{host}:{port}/v1/messages")
    print(f"Model List:          http://{host}:{port}/v1/models")
    print(f"Health Check:        http://{host}:{port}/health")
    print("=" * 85)
    uvicorn.run(app, host=host, port=port, log_level="info")

if __name__ == "__main__":
    run()
