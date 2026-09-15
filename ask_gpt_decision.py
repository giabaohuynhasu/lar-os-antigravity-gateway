import sys
import urllib.request
import json
import asyncio
from opera_neon_ai_bridge import OperaNeonBridge

if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8")

async def main():
    if len(sys.argv) < 2:
        print("Usage: python ask_gpt_decision.py '<question>'")
        sys.exit(1)

    bridge = OperaNeonBridge()
    if not bridge.is_alive():
        print("[-] Opera Neon is not reachable on CDP port 9224")
        return

    prompt = sys.argv[1]

    print("[*] Sending consultation to ChatGPT in Opera Neon...")
    res = await bridge.consult_ai("chatgpt", prompt, timeout_seconds=90)
    print("\n=== KẾT QUẢ TỪ CHATGPT ===")
    print(res.get("text", json.dumps(res, ensure_ascii=False, indent=2)))

if __name__ == "__main__":
    asyncio.run(main())
