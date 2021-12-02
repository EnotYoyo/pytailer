from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from pytailer import FileTail
from utils import EndTest, write_to_end

pytestmark = pytest.mark.timeout(1)


def test_tail_lines(tmp_path: Path):
    tmp_file = tmp_path / "file.txt"
    tmp_file.write_text("hello\nworld\n")

    file_tail_iter = FileTail(tmp_file, lines=1).tail()
    assert next(file_tail_iter) == "world\n"

    file_tail_iter = FileTail(tmp_file, lines=2).tail()
    assert next(file_tail_iter) == "hello\n"
    assert next(file_tail_iter) == "world\n"


def test_tail_simple(tmp_path: Path):
    tmp_file = tmp_path / "file.txt"
    tmp_file.write_text("hello\n")

    file_tail_iter = FileTail(tmp_file, lines=1).tail()
    assert next(file_tail_iter) == "hello\n"

    test_line = "test line\n"
    write_to_end(tmp_file, test_line)

    assert next(file_tail_iter) == test_line


def test_tail_file_wait_data(tmp_path: Path, mocker: MockerFixture):
    mocker.patch("time.sleep", side_effect=[3, 2, 1, EndTest()])
    tmp_file = tmp_path / "file.txt"

    file_tail_iter = iter(FileTail(tmp_file))
    with pytest.raises(EndTest):
        next(file_tail_iter)


def test_tail_file_as_context_manager(tmp_path: Path):
    tmp_file = tmp_path / "file.txt"
    tmp_file.write_text("hello\n")

    with FileTail(tmp_file, lines=1) as tail:
        for line in tail:
            assert line == "hello\n"
            break

    assert tail._file._current_file is None  # noqa: the real descriptor has been closed
