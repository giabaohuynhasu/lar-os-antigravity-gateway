#!/usr/bin/env python3
"""
🌐 Antigravity Cloudflare Tunnel Bridge (tunnel_bridge.py)
Creates an instant, secure, public HTTPS tunnel for ChatGPT Custom Actions, Mobile, and Webhooks.

Saves public URL to:
- local TUNNEL_URL.txt
- Google Drive: G:\\Drive của tôi\\Gemini_Spark_Bridge\\CHATGPT_ACTION_URL.txt
- Exports tailored chatgpt_actions_openapi.json with the live server URL.
"""

import os
import sys
import time
import re
import json
import subprocess
from pathlib import Path

if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8")

GATEWAY_PORT = 18797

SCRATCH_DIR = Path(__file__).resolve().parent
CLOUDFLARED_BIN = Path(r"C:\Users\nswcl\bin\cloudflared.exe")
DRIVE_DIR = Path(r"G:\Drive của tôi\Gemini_Spark_Bridge")

def generate_chatgpt_openapi(public_url: str):
    schema = {
        "openapi": "3.1.0",
        "info": {
            "title": "Antigravity Autonomous Operating System API",
            "description": "Connects ChatGPT mobile/web to Gia Bao Huynh's Antigravity Autonomous Engine (5-Pro Key Quota Pool, Opera Neon Claude/ChatGPT, and Gmail Dispatcher).",
            "version": "3.5.0"
        },
        "servers": [
            {"url": public_url, "description": "Antigravity Cloudflare Secure Tunnel"}
        ],
        "paths": {
            "/v1/chat/completions": {
                "post": {
                    "summary": "Execute Prompt with Antigravity AI Engine",
                    "description": "Dispatches prompt to Antigravity 5-Pro Quota Pool, Claude Sonnet 5 Max, or ChatGPT on Opera Neon. Optionally sends HTML report to user's Gmail.",
                    "operationId": "askAntigravity",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "model": {
                                            "type": "string",
                                            "enum": ["gemini-3.5-flash", "gemini-3.5-pro", "claude", "chatgpt"],
                                            "default": "gemini-3.5-flash",
                                            "description": "Model engine to process the request."
                                        },
                                        "messages": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "role": {"type": "string", "enum": ["user", "system", "assistant"]},
                                                    "content": {"type": "string"}
                                                },
                                                "required": ["role", "content"]
                                            },
                                            "description": "Chat messages history or prompt."
                                        },
                                        "send_email": {
                                            "type": "boolean",
                                            "default": False,
                                            "description": "If true, automatically formats and dispatches an HTML report to thuaquan228@gmail.com."
                                        }
                                    },
                                    "required": ["messages"]
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Execution successful",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "choices": {
                                                "type": "array",
                                                "items": {
                                                    "type": "object",
                                                    "properties": {
                                                        "message": {
                                                            "type": "object",
                                                            "properties": {
                                                                "content": {"type": "string"}
                                                            }
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/health": {
                "get": {
                    "summary": "Check Antigravity System Health",
                    "description": "Returns health status of Gateway, 5 Google Pro Keys, Opera Neon, and Drive Bridge.",
                    "operationId": "checkSystemHealth",
                    "responses": {
                        "200": {
                            "description": "System health payload",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object"
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    
    out_path = SCRATCH_DIR / "chatgpt_actions_openapi.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=2, ensure_ascii=False)
    print(f"[✓] Generated ChatGPT Actions Schema: {out_path}")

    # Also save to Drive if available
    if DRIVE_DIR.exists():
        drive_schema = DRIVE_DIR / "chatgpt_actions_openapi.json"
        with open(drive_schema, "w", encoding="utf-8") as f:
            json.dump(schema, f, indent=2, ensure_ascii=False)
        print(f"[✓] Synced ChatGPT OpenAPI Schema to Google Drive: {drive_schema}")

def run_tunnel():
    if not CLOUDFLARED_BIN.exists():
        print(f"[-] Error: cloudflared not found at {CLOUDFLARED_BIN}")
        return

    cmd = [
        str(CLOUDFLARED_BIN),
        "tunnel",
        "--url", f"http://127.0.0.1:{GATEWAY_PORT}",
        "--no-autoupdate"
    ]
    print(f"[+] Starting Cloudflare Quick Tunnel on port {GATEWAY_PORT}...")
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        bufsize=1
    )

    tunnel_url = None
    url_pattern = re.compile(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com")

    for line in proc.stdout:
        # print line for logs
        if "trycloudflare.com" in line:
            match = url_pattern.search(line)
            if match:
                tunnel_url = match.group(0)
                print("\n" + "=" * 65)
                print(f"🚀 CLOUDFLARE LIVE HTTPS TUNNEL ESTABLISHED! 🚀")
                print(f"Public URL: {tunnel_url}")
                print("=" * 65 + "\n")

                # Save local
                with open(SCRATCH_DIR / "TUNNEL_URL.txt", "w", encoding="utf-8") as f:
                    f.write(tunnel_url)

                # Save to Google Drive
                if DRIVE_DIR.exists():
                    with open(DRIVE_DIR / "ANTIGRAVITY_CHATGPT_URL.txt", "w", encoding="utf-8") as f:
                        f.write(tunnel_url)

                # Generate OpenAPI schema for Custom GPT
                generate_chatgpt_openapi(tunnel_url)
                break

    # Keep running
    proc.wait()

if __name__ == "__main__":
    run_tunnel()
