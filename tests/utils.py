from pathlib import Path
from typing import Any, AnyStr, AsyncIterable, AsyncIterator, TypeVar, Union

_default = object()
_T = TypeVar("_T")


class EndTest(Exception):
    ...


def write_to_end(file: Path, line: AnyStr):
    with file.open("a") as io:
        io.write(line)


def aiter(iterable: AsyncIterable[_T]) -> AsyncIterator[_T]:
    return iterable.__aiter__()


async def anext(async_iter: AsyncIterator[_T], default: Any = _default) -> Union[_T, Any]:
    try:
        return await async_iter.__anext__()
    except StopAsyncIteration:
        if default is not _default:
            return default
        else:
            raise
