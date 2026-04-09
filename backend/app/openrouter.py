import os
from typing import Any, Optional

import httpx

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL_NAME = "openai/gpt-oss-120b"


def call_openrouter(prompt: str, timeout: float = 30.0) -> str:
    messages = [{"role": "user", "content": prompt}]
    return call_openrouter_messages(messages, timeout=timeout)


def call_openrouter_messages(
    messages: list[dict[str, str]],
    timeout: float = 30.0,
    response_format: Optional[dict[str, Any]] = None,
) -> str:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY is not set")

    payload: dict[str, Any] = {
        "model": MODEL_NAME,
        "messages": messages,
        "temperature": 0.1,
    }
    if response_format is not None:
        payload["response_format"] = response_format

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    with httpx.Client(timeout=timeout) as client:
        response = client.post(OPENROUTER_URL, json=payload, headers=headers)
        response.raise_for_status()
        data: dict[str, Any] = response.json()

    content = _extract_content(data)
    if content is None:
        raise RuntimeError("No content returned from OpenRouter")
    return content


def _extract_content(data: dict[str, Any]) -> Optional[str]:
    choices = data.get("choices")
    if not choices:
        return None
    message = choices[0].get("message") if isinstance(choices[0], dict) else None
    if not message:
        return None
    content = message.get("content")
    if isinstance(content, str):
        return content
    return None
