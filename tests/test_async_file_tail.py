import asyncio
import sys
from pathlib import Path
from typing import Any

import pytest
from pytest_mock import MockerFixture

from pytailer import AsyncFileTail
from utils import EndTest, aiter, anext, write_to_end

pytestmark = [pytest.mark.asyncio, pytest.mark.timeout(100000)]


async def test_async_tail_lines(tmp_path: Path):
    tmp_file = tmp_path / "file.txt"
    tmp_file.write_text("hello\nworld\n")

    file_tail_iter = AsyncFileTail(tmp_file, lines=1).tail()
    assert await anext(file_tail_iter) == "world\n"

    file_tail_iter = AsyncFileTail(tmp_file, lines=2).tail()
    assert await anext(file_tail_iter) == "hello\n"
    assert await anext(file_tail_iter) == "world\n"


async def test_async_tail_simple(tmp_path: Path):
    tmp_file = tmp_path / "file.txt"
    tmp_file.write_text("hello\n")

    file_tail_iter = AsyncFileTail(tmp_file, lines=1).tail()
    assert await anext(file_tail_iter) == "hello\n"

    test_line = "test line\n"
    write_to_end(tmp_file, test_line)

    assert await anext(file_tail_iter) == test_line


async def test_async_tail_file_wait_data(tmp_path: Path, mocker: MockerFixture):
    def _awaitable(value: Any):
        # for python 3.8+ mocker will be use AsyncMock
        if sys.version_info >= (3, 8):
            return value

        # simple awaitable wrapper for 3.7- side_effect
        future = asyncio.Future()
        if isinstance(value, Exception):
            future.set_exception(value)
        else:
            future.set_result(value)
        return future

    mocker.patch("asyncio.sleep", side_effect=[_awaitable(3), _awaitable(2), _awaitable(1), _awaitable(EndTest())])
    tmp_file = tmp_path / "file.txt"
    file_tail_iter = aiter(AsyncFileTail(tmp_file))
    with pytest.raises(EndTest):
        await anext(file_tail_iter)


async def test_async_tail_file_as_context_manager(tmp_path: Path):
    tmp_file = tmp_path / "file.txt"
    tmp_file.write_text("hello\n")

    with AsyncFileTail(tmp_file, lines=1) as tail:
        async for line in tail:
            assert line == "hello\n"
            break

    assert tail._file._current_file is None  # noqa: the real descriptor has been closed


async def test_async_tail_file_as_sync_version(tmp_path: Path):
    tmp_file = tmp_path / "file.txt"
    tmp_file.write_text("hello\n")

    with AsyncFileTail(tmp_file, lines=1) as tail:
        for line in tail:
            assert line == "hello\n"
            break
