
from typing import Dict, List
import httpx
import asyncio
import re

from app.config import settings


def _messages(system_prompt: str, history: List[Dict], user_message: str) -> List[Dict]:
    # Telugu can consume more model tokens per character than English. Keep a
    # conservative character budget before the request reaches Groq.
    system_prompt = (system_prompt or "")[:settings.MAX_SYSTEM_CHARS]
    user_message = (user_message or "")[:settings.MAX_USER_CHARS]
    messages = [{"role": "system", "content": system_prompt}]
    per_turn_cap = settings.max_history_chars_per_turn
    for item in (history or [])[-settings.max_history_turns:]:
        if not isinstance(item, dict):
            continue
        role = item.get("role")
        content = item.get("content")
        if role in {"user", "assistant"} and isinstance(content, str) and content.strip():
            messages.append({"role": role, "content": content.strip()[:per_turn_cap]})
    messages.append({"role": "user", "content": user_message.strip()})
    return messages


async def call_groq(system_prompt: str, history: List[Dict], user_message: str) -> str:
    if not settings.groq_token:
        raise RuntimeError("GROQ_TOKEN is not set.")

    payload = {
        "model": settings.groq_model,
        "messages": _messages(system_prompt, history, user_message),
        "temperature": settings.temperature,
        "top_p": 0.92,
        "max_tokens": settings.max_response_tokens,
    }
    headers = {
        "Authorization": f"Bearer {settings.groq_token}",
        "Content-Type": "application/json",
    }

    timeout = httpx.Timeout(connect=10, read=60, write=30, pool=10)

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(settings.groq_url, json=payload, headers=headers)
    except httpx.TimeoutException as exc:
        raise RuntimeError("Groq API request timed out.") from exc
    except httpx.RequestError as exc:
        raise RuntimeError(f"Unable to connect to Groq API: {exc}") from exc

    if response.status_code != 200:
        if response.status_code == 413:
            raise RuntimeError("Groq request is too large for the current TPM/model limit. The app has already reduced context; shorten the user message or lower the model/context limits.")
        if response.status_code == 429:
            raise RuntimeError(_rate_limit_message(response))
        if response.status_code in (401, 403):
            raise RuntimeError("Groq API authentication failed. Check GROQ_TOKEN.")
        try:
            detail = response.json()
        except Exception:
            detail = response.text
        raise RuntimeError(f"Groq API error {response.status_code}: {detail}")

    try:
        data = response.json()
        answer = data["choices"][0]["message"]["content"]
    except Exception as exc:
        raise RuntimeError("Groq returned an invalid response.") from exc

    answer = str(answer or "").strip()
    if not answer:
        raise RuntimeError("Groq returned an empty response.")
    return answer


def _duration_seconds(value: str | None) -> float | None:
    if not value:
        return None
    value = value.strip()
    # Groq may return seconds ("34s"), milliseconds ("1ms"), or a compact
    # duration such as "1m20s". Convert everything to seconds for users.
    total = 0.0
    matched = False
    for num, unit in re.findall(r"([0-9]+(?:\.[0-9]+)?)(ms|h|m|s)", value):
        matched = True
        n = float(num)
        total += n / 1000 if unit == "ms" else n * {"s":1,"m":60,"h":3600}[unit]
    if matched:
        return total
    try:
        return float(value)
    except ValueError:
        return None


def _rate_limit_message(response: httpx.Response) -> str:
    h = response.headers
    retry_after = h.get("retry-after")
    reset_requests = h.get("x-ratelimit-reset-requests")
    reset_tokens = h.get("x-ratelimit-reset-tokens")
    wait = _duration_seconds(retry_after) or _duration_seconds(reset_tokens) or _duration_seconds(reset_requests)
    if wait is not None:
        wait_text = f"{max(1, round(wait))} seconds" if wait < 60 else f"{round(wait/60, 1)} minutes"
        return f"Groq is temporarily rate-limited. Please try again in about {wait_text}."
    return "Groq is temporarily rate-limited. Please wait a short time and try again."
