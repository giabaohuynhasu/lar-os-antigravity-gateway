"""
google_ai_studio_client.py -- Google AI Studio & Gemini API Client for LAR-OS & Google Jules.

Empowers Google Jules and Antigravity with direct access to Google AI Studio
(models/gemini-3.6-flash, models/gemini-3.5-flash, models/gemini-2.5-pro) for:
  1. Synthetic data and test fixture generation.
  2. SPEC.md Section 2: Automated LLM paper extraction into ResearchObject schema.
  3. Evidence verification, citation cross-checking, and anti-sycophancy audits.

Author: Gia Bao Huynh (Jun) · Antigravity Research OS
"""

import os
import sys
import json
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, Any, Optional, List

if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent
KEYS_FILE = BASE_DIR / "gateway_keys.json"
DEFAULT_MODEL = "gemini-3.6-flash"
API_BASE = "https://generativelanguage.googleapis.com/v1beta/models"


class GoogleAIStudioClient:
    """Client for Google AI Studio with automated key rotation and quota resilience."""

    def __init__(self, key_file: Optional[Path] = None, model: str = DEFAULT_MODEL):
        self.key_file = key_file or KEYS_FILE
        self.model = model
        self.keys = self._load_keys()
        self._key_idx = 0

    def _load_keys(self) -> List[Dict[str, Any]]:
        # 1. Check environment
        env_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if env_key:
            return [{"key": env_key, "account": "ENV_DEFAULT", "status": "ACTIVE"}]

        # 2. Check gateway_keys.json
        if self.key_file.exists():
            try:
                with open(self.key_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return [k for k in data.get("api_keys", []) if k.get("status") == "ACTIVE" and k.get("key")]
            except Exception as e:
                print(f"[!] Warning: failed loading keys from {self.key_file}: {e}")

        # 3. Check scratch location
        scratch_keys = Path(r"C:\Users\nswcl\.gemini\antigravity-ide\scratch\gateway_keys.json")
        if scratch_keys.exists():
            try:
                with open(scratch_keys, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return [k for k in data.get("api_keys", []) if k.get("status") == "ACTIVE" and k.get("key")]
            except Exception:
                pass

        return []

    def get_active_key(self) -> str:
        if not self.keys:
            raise RuntimeError("No active Google AI Studio keys available in gateway_keys.json or environment.")
        k = self.keys[self._key_idx % len(self.keys)]["key"]
        self._key_idx += 1
        return k

    def generate_content(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.2,
        max_output_tokens: int = 2048,
        response_schema: Optional[Dict[str, Any]] = None,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """Calls Google AI Studio v1beta generateContent API with failover."""
        target_model = model or self.model
        last_error = None

        for attempt in range(len(self.keys) or 1):
            key = self.get_active_key()
            url = f"{API_BASE}/{target_model}:generateContent?key={key}"

            payload: Dict[str, Any] = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": temperature,
                    "maxOutputTokens": max_output_tokens
                }
            }

            if system_instruction:
                payload["systemInstruction"] = {
                    "parts": [{"text": system_instruction}]
                }

            if response_schema:
                payload["generationConfig"]["responseMimeType"] = "application/json"
                payload["generationConfig"]["responseSchema"] = response_schema

            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )

            try:
                with urllib.request.urlopen(req, timeout=20) as resp:
                    if resp.status == 200:
                        data = json.loads(resp.read().decode("utf-8"))
                        text = data["candidates"][0]["content"]["parts"][0]["text"]
                        return {
                            "text": text,
                            "model": target_model,
                            "raw": data
                        }
            except urllib.error.HTTPError as e:
                err_body = e.read().decode("utf-8", errors="ignore")
                last_error = f"HTTP {e.code}: {err_body}"
                if e.code in (429, 403):
                    continue  # rotate to next key
                raise RuntimeError(f"Google AI Studio Error ({target_model}): {last_error}")
            except Exception as e:
                last_error = str(e)
                continue

        raise RuntimeError(f"All Google AI Studio keys exhausted. Last error: {last_error}")

    def extract_research_object(self, paper_text: str, paper_id: str = "extracted_paper") -> Dict[str, Any]:
        """
        Implements SPEC.md Section 2:
        Uses Google AI Studio to extract an honest ResearchObject conforming to
        Huynh (2026) Third-Order Audit schema with mandatory source_note and confidence labels.
        """
        sys_prompt = """You are an expert scientific epistemologist performing a Third-Order Audit.
Extract a structured ResearchObject from the provided paper text.
Rules:
1. State each falsification condition's exact text from the paper (do NOT paraphrase).
2. Set references_external_source=true ONLY if it points to a dated event, independent publication, or primary data.
3. Classify revisions categorically: narrowed, withdrawn, reaffirmed, or extended.
4. Mandatory source_note: Explain who coded it and against what record.
5. Set confidence label: HIGH, MEDIUM, LOW, or UNVERIFIED."""

        prompt = f"""PAPER ID: {paper_id}
PAPER TEXT:
{paper_text[:6000]}

Propose a valid ResearchObject JSON conforming to the sandbox.py template:
{{
  "id": "{paper_id}",
  "title": "<title>",
  "falsification_conditions": [
    {{
      "id": "F-1",
      "text": "<exact text>",
      "references_external_source": true,
      "source_note": "<justification>",
      "confidence": "HIGH",
      "external_anchor": "<doi or url>"
    }}
  ],
  "revisions": [
    {{
      "delta_type": "narrowed",
      "trigger": "<trigger>",
      "note": "<note>",
      "source_note": "<justification>",
      "confidence": "HIGH",
      "external_anchor": "<anchor>"
    }}
  ],
  "self_referential_audit_present": false
}}"""

        res = self.generate_content(prompt=prompt, system_instruction=sys_prompt)
        text = res["text"].strip()
        # Clean markdown formatting if present
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return json.loads(text.strip())


# Default singleton instance
ai_studio_client = GoogleAIStudioClient()


if __name__ == "__main__":
    print("Testing Google AI Studio Client...")
    try:
        reply = ai_studio_client.generate_content("Ping. Reply in 1 sentence confirming AI Studio connection.")
        print("Response:", reply["text"])
    except Exception as e:
        print("Error:", e)
