import asyncio
import sys
from opera_neon_ai_bridge import get_bridge

if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8")

async def get_full():
    bridge = get_bridge()
    tab = bridge.get_or_create_tab('chatgpt.com', 'https://chatgpt.com/')
    ws_url = tab['webSocketDebuggerUrl']
    js = """
    (function() {
        var articles = document.querySelectorAll('article, div[data-message-author-role="assistant"]');
        var last = articles[articles.length - 1];
        return last ? last.innerText : '';
    })()
    """
    text = await bridge.evaluate_js(ws_url, js)
    print("FULL_LEN:", len(text))
    with open("chatgpt_phase8_9_11_consultation.txt", "w", encoding="utf-8") as f:
        f.write(text)
    print("Updated chatgpt_phase8_9_11_consultation.txt")

asyncio.run(get_full())
