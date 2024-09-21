import uuid
from abc import ABC, abstractmethod
from typing import Tuple, List


class AsyncSearchEngine(ABC):
    @abstractmethod
    async def get_by_id(self, index: str, _id: uuid) -> dict:
        pass

    @abstractmethod
    async def get_list(
        self,
        index: str,
        page_size: int,
        page_number: int,
        sort_order: str | None = None,
        sort_field: str | None = None,
        query: str | None = None,
    ) -> Tuple[List, int]:
        pass
