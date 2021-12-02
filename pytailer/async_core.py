import asyncio
import logging
from typing import AnyStr, AsyncGenerator

from .core import FileTail

logger = logging.getLogger(__name__)


class AsyncFileTail(FileTail):

    async def tail(self) -> AsyncGenerator[AnyStr, None]:
        logger.debug("Tail for %s", self._file.path)

        if not self._read_all:
            for line in self._file.read_last_lines(self._lines):
                yield line

        while True:
            line = self._file.readline()
            if not line:
                await asyncio.sleep(self._check_delay)
            else:
                yield line

    def __iter__(self):
        return super().tail()

    def __aiter__(self):
        return self.tail()


async_fail_tail = AsyncFileTail  # alias
