from __future__ import annotations

from dataclasses import dataclass

from fastapi import Request

FLASH_SESSION_KEY = "flash_messages"


@dataclass(frozen=True)
class FlashMessage:
    message: str
    category: str = "info"


def flash(request: Request, message: str, category: str = "info") -> None:
    messages = request.session.get(FLASH_SESSION_KEY)
    if not isinstance(messages, list):
        messages = []
    messages.append({"message": message, "category": category})
    request.session[FLASH_SESSION_KEY] = messages


def get_flashed_messages(request: Request) -> list[FlashMessage]:
    raw_messages = request.session.pop(FLASH_SESSION_KEY, [])
    if not isinstance(raw_messages, list):
        return []

    messages: list[FlashMessage] = []
    for item in raw_messages:
        if isinstance(item, dict) and isinstance(item.get("message"), str):
            category = item.get("category")
            messages.append(
                FlashMessage(
                    message=item["message"],
                    category=category if isinstance(category, str) else "info",
                )
            )
    return messages
