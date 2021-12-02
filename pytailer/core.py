import logging
import os
import time
from pathlib import Path
from typing import AnyStr, Generator, List, Optional, TextIO, Union

logger = logging.getLogger(__name__)


class MutableFile:
    ends_of_line = "\r", "\n"

    def __init__(self, path: Union[AnyStr, Path], **open_kwargs):
        self.path = Path(path)
        self._open_kwargs = open_kwargs
        self._current_file: Optional[TextIO] = None
        self._current_file_stat: Optional[os.stat_result] = None

    @property
    def _same_stat(self) -> bool:
        try:
            current_stat = self.path.stat()
        except OSError:
            # the current file is the latest version of the file
            return True
        return os.path.samestat(self._current_file_stat, current_stat)

    @property
    def _is_outdated(self) -> bool:
        return self._current_file is None or not self._same_stat

    def _reopen_if_outdated(self):
        if self._is_outdated:
            logger.debug("Current file is outdated")
            self.open()
        return not self._is_outdated

    def open(self) -> "MutableFile":
        logger.debug("Try to open %s", self.path)

        # close old descriptor before re-open
        self.close()
        try:
            self._current_file = self.path.open(**self._open_kwargs)
            self._current_file_stat = os.stat(self._current_file.fileno())
        except OSError as e:
            logger.debug("Can't open file %s", str(e))

        return self

    def close(self):
        if self._current_file and not self._current_file.closed:
            self._current_file.close()
            self._current_file = None
            self._current_file_stat = None

    def seek(self, offset: int, whence: int = os.SEEK_SET):
        self._current_file.seek(offset, whence)

    def read_last_lines(self, num: int = 0, buffer_length: int = 4096) -> List[AnyStr]:
        logger.debug("Read last %d lines from %s", num, self.path)

        if not self._reopen_if_outdated():
            return []

        current_offset, lines = buffer_length, []
        self.seek(0, os.SEEK_END)

        # trying to find the offset to read num lines from file
        while num and len(lines) <= num:
            try:
                self.seek(self._current_file.tell() - current_offset)
            except (IOError, ValueError):
                logger.debug("Read all lines from file")
                self.seek(0)
                break
            finally:
                lines = self._current_file.readlines()

            current_offset += buffer_length

        return lines[-num:]

    def readline(self) -> AnyStr:
        if not self._reopen_if_outdated():
            return ""

        prev_position = self._current_file.tell()
        line = self._current_file.readline()

        if line and line[-1] in self.ends_of_line:
            return line
        else:
            self.seek(prev_position)
            return ""


class FileTail:

    def __init__(
            self,
            file: Union[AnyStr, Path],
            read_all: bool = False,
            lines: int = 0,
            check_delay: float = 1,
            **open_kwargs,
    ):
        assert lines >= 0

        self._file = MutableFile(file, **open_kwargs)
        self._lines = lines
        self._read_all = read_all
        self._check_delay = check_delay

    def tail(self) -> Generator[AnyStr, None, None]:
        logger.debug("Tail for %s", self._file.path)

        if not self._read_all:
            yield from self._file.read_last_lines(self._lines)

        while True:
            line = self._file.readline()
            if not line:
                time.sleep(self._check_delay)
            else:
                yield line

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._file.close()

    def __iter__(self):
        return self.tail()


fail_tail = FileTail  # alias
