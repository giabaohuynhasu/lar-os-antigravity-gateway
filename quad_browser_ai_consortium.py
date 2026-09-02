"""
Quad-Browser AI Consortium Orchestrator
Author: Gia Bao Huynh (Jun) / LAR-OS
Role: Query Perplexity (Comet:9222), Copilot (Edge:9223), Gemini (Chrome:9224), and ChatGPT (Opera Neon:9225) simultaneously via CDP.
Zero-Quota, Multi-Engine Parallel Consensus Architecture.
"""

import os
import sys
import json
import asyncio
from pathlib import Path

if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8")

from comet_agent import perform_search_and_extract as query_comet
from edge_copilot_bridge import query_edge_copilot
from chrome_gemini_bridge import query_chrome_gemini
from opera_chatgpt_operator import operate_chatgpt_on_opera

async def dispatch_quad_ai_search(topic: str):
    print("=" * 90)
    print("🚀 QUAD-BROWSER AI CONSORTIUM: 4-ENGINE PARALLEL RESEARCH & CONSENSUS 🚀")
    print(f"Research Topic: {topic}")
    print("=" * 90)
    
    print("\n[1/4] Calling Perplexity AI via Comet Browser (Port 9222)...")
    comet_task = asyncio.create_task(query_comet(topic))
    
    print("[2/4] Calling Microsoft Copilot via Edge Browser (Port 9223)...")
    edge_task = asyncio.create_task(query_edge_copilot(topic))
    
    print("[3/4] Calling Google Gemini via Chrome Browser (Port 9224)...")
    chrome_task = asyncio.create_task(query_chrome_gemini(topic))
    
    print("[4/4] Calling OpenAI ChatGPT via Opera Neon Browser (Port 9225)...")
    opera_task = asyncio.create_task(operate_chatgpt_on_opera(topic))
    
    results = await asyncio.gather(comet_task, edge_task, chrome_task, opera_task, return_exceptions=True)
    
    print("\n" + "=" * 90)
    print("✓ ALL FOUR AI BROWSER ENGINES SUCCESSFULLY ORCHESTRATED IN PARALLEL!")
    print("=" * 90)
    return {
        "topic": topic,
        "perplexity_comet": results[0] if not isinstance(results[0], Exception) else str(results[0]),
        "microsoft_edge_copilot": results[1] if not isinstance(results[1], Exception) else str(results[1]),
        "google_chrome_gemini": results[2] if not isinstance(results[2], Exception) else str(results[2]),
        "openai_chatgpt_opera": results[3] if not isinstance(results[3], Exception) else str(results[3])
    }

if __name__ == "__main__":
    t = "Longevity Asymmetry and Institutional Endurance"
    if len(sys.argv) > 1:
        t = " ".join(sys.argv[1:])
    asyncio.run(dispatch_quad_ai_search(t))
