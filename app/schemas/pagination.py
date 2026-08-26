from typing import TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PageResponse[T](BaseModel):
    items: list[T]
    page: int
    limit: int
    total: int
    has_next: bool
