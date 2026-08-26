from dataclasses import dataclass
from typing import TypeVar

T = TypeVar("T")


@dataclass(slots=True)
class PageResult[T]:
    items: list[T]
    page: int
    limit: int
    total: int

    @property
    def has_next(self) -> bool:
        return self.page * self.limit < self.total
