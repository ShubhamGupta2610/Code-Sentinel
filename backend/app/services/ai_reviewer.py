"""Core AI reviewer pipeline with CoT, RAG context, and resilient JSON parsing."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List

import httpx

from app.core.config import settings
from app.core.exceptions import AIReviewError
from app.core.logger import get_logger

logger = get_logger(service="ai-reviewer")


def _call_llm(prompt: str) -> str:
    """Call Groq LLM."""
    try:
        with httpx.Client(timeout=httpx.Timeout(180.0, connect=10.0)) as client:
            resp = client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.GROQ_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are an expert secure code reviewer. Return valid JSON only."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.2,
                },
            )

            resp.raise_for_status()
            data = resp.json()

            return data["choices"][0]["message"]["content"]

    except Exception as exc:
        logger.error("groq_request_failed", error=str(exc))
        raise


def _parse_json_layers(raw: str, chunk_index: int) -> Dict[str, Any]:
    """Three-layer JSON recovery strategy."""
    # Layer 1: direct parse
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        logger.debug("json_parse_failed_direct", chunk_index=chunk_index)

    # Layer 2: regex extraction of first JSON object
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            logger.debug("json_parse_failed_regex", chunk_index=chunk_index)

    # Layer 3: instruct model to emit strict JSON only
    strict_prompt = (
        "You returned malformed JSON. "
        "Reformat the previous content into STRICT JSON with keys: "
        "reasoning_summary (string) and findings (array of objects: "
        "severity, category, file_path, line, issue, attack_scenario, fix, confidence). "
        "Return ONLY JSON. Here is your prior output:\n"
        f"{raw}"
    )
    retry_raw = _call_llm(strict_prompt)
    try:
        return json.loads(retry_raw)
    except json.JSONDecodeError as exc:  # noqa: BLE001
        raise AIReviewError(chunk_index=chunk_index, raw_output=retry_raw, attempts_made=3) from exc


def _load_prompt_assets() -> tuple[str, str]:
    """Load system and OWASP exemplar prompts from disk."""
    root = Path(__file__).resolve().parents[3]  # repo root (CodeSentinel)
    system_prompt = (root / "prompts" / "system_prompt.txt").read_text(encoding="utf-8")
    owasp_examples = (root / "prompts" / "security_prompt.txt").read_text(encoding="utf-8")[:500]
    return system_prompt, owasp_examples


def _build_prompt(intent_summary: str, context_block: str, owasp_examples: str, system_prompt: str, chunk: str) -> str:
    """Compose the full CoT prompt in mandated order."""
    return "\n\n".join(
        [
            system_prompt.strip(),
            "## Developer Intent\n" + intent_summary.strip(),
            "## File Context (RAG)\n" + context_block.strip(),
            "## OWASP Examples\n" + owasp_examples.strip(),
            "## Code Diff To Review\n"
            "Follow the 4-step Chain-of-Thought:\n"
            "1) Intent understanding\n"
            "2) Line-by-line analysis\n"
            "3) OWASP mapping\n"
            "4) Fix generation\n"
            f"{chunk}",
        ]
    )


def _normalize_findings(parsed: Dict[str, Any]) -> tuple[str, List[Dict[str, Any]]]:
    reasoning = parsed.get("reasoning_summary", "") if isinstance(parsed, dict) else ""
    findings = parsed.get("findings", []) if isinstance(parsed, dict) else []
    normalized: List[Dict[str, Any]] = []
    for item in findings:
        if not isinstance(item, dict):
            continue
        normalized.append(
            {
                "severity": item.get("severity"),
                "category": item.get("category"),
                "file_path": item.get("file_path"),
                "line": item.get("line") or item.get("line_number") or 1,
                "issue": item.get("issue") or item.get("issue_text"),
                "attack_scenario": item.get("attack_scenario"),
                "fix": item.get("fix") or item.get("fix_suggestion"),
                "confidence": float(item.get("confidence", 0.0)),
            }
        )
    return reasoning, normalized


def review_chunk(chunk: str, intent_summary: str, context_block: str, chunk_index: int | None = None) -> Dict[str, Any]:
    """Run CoT-guided review on a diff chunk."""
    idx = chunk_index if chunk_index is not None else -1
    system_prompt, owasp_examples = _load_prompt_assets()
    prompt = _build_prompt(intent_summary, context_block, owasp_examples, system_prompt, chunk)

    token_estimate = max(1, len(prompt) // 4)
    logger.debug(EVENT["LLM_CALL_STARTED"], chunk_index=idx, model=settings.OLLAMA_MODEL, token_estimate=token_estimate)
    try:
        raw = _call_llm(prompt)
        logger.debug(EVENT["LLM_RESPONSE_RECEIVED"], chunk_index=idx, raw_output_length=len(raw))
    except Exception:
        # Optional OpenAI fallback
        if settings.OPENAI_API_KEY:
            logger.warning("ollama_failed_using_openai", chunk_index=idx)
            raw = _call_openai(prompt, chunk_index=idx)
        else:
            raise

    parsed = _parse_json_layers(raw, chunk_index=idx)
    reasoning, findings = _normalize_findings(parsed)

    # Do not drop lower-confidence findings here; filtering is applied downstream for posting.
    return {"reasoning_summary": reasoning, "findings": findings}


def _call_openai(prompt: str, chunk_index: int) -> str:
    """Fallback to OpenAI chat completion if configured."""
    import json as _json

    headers = {
        "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "system", "content": "Return only JSON"}, {"role": "user", "content": prompt}],
        "temperature": 0.2,
    }
    with httpx.Client(timeout=httpx.Timeout(60.0, connect=10.0)) as client:
        resp = client.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        try:
            resp.raise_for_status()
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
            logger.debug(EVENT["LLM_RESPONSE_RECEIVED"], provider="openai", chunk_index=chunk_index, raw_output_length=len(content))
            return content
        except Exception as exc:  # noqa: BLE001
            logger.error("openai_request_failed", error=str(exc))
            raise AIReviewError(chunk_index=chunk_index, raw_output=resp.text if resp else "", attempts_made=3) from exc


def filter_findings(findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Apply global confidence threshold."""
    threshold = settings.CONFIDENCE_THRESHOLD
    return [f for f in findings if float(f.get("confidence", 0.0)) >= threshold]
