import sys
from pathlib import Path

import pytest

from pytailer.core import MutableFile
from utils import write_to_end


def test_mutable_file_create(tmp_path: Path):
    tmp_file = tmp_path / "file.txt"
    mutable_file = MutableFile(tmp_file)
    assert mutable_file.path == tmp_file


def test_mutable_file_open_not_exists(tmp_path: Path):
    tmp_file = tmp_path / "file.txt"

    mutable_file = MutableFile(tmp_file)
    mutable_file.open()
    assert mutable_file._current_file is None


def test_mutable_file_open_exists(tmp_path: Path):
    tmp_file = tmp_path / "file.txt"
    tmp_file.touch()

    mutable_file = MutableFile(tmp_file)
    mutable_file.open()
    assert mutable_file._current_file is not None


def test_mutable_file_read_last_lines(tmp_path: Path):
    tmp_file = tmp_path / "file.txt"
    tmp_file.write_text("hello\nworld\n")

    mutable_file = MutableFile(tmp_file)

    assert mutable_file.read_last_lines(1) == ["world\n"]
    assert mutable_file.read_last_lines(2) == ["hello\n", "world\n"]
    assert mutable_file.read_last_lines(10) == ["hello\n", "world\n"]
    assert mutable_file.read_last_lines(0) == []


def test_mutable_file_read_last_lines_from_empty_file(tmp_path: Path):
    tmp_file = tmp_path / "file.txt"
    tmp_file.touch()

    mutable_file = MutableFile(tmp_file)

    assert mutable_file.read_last_lines(10) == []
    assert mutable_file.read_last_lines(0) == []


def test_mutable_file_read_last_lines_file_not_exists(tmp_path: Path):
    tmp_file = tmp_path / "file.txt"

    mutable_file = MutableFile(tmp_file)

    assert mutable_file.read_last_lines(10) == []
    assert mutable_file.read_last_lines(0) == []


def test_mutable_file_read_last_lines_with_offset(tmp_path: Path):
    tmp_file = tmp_path / "test_read_large_file.txt"
    data = ("a" * 9 + "\n") * 10
    data += ("b" * 10 + "\n") * 10
    tmp_file.write_text(data)

    mutable_file = MutableFile(tmp_file)
    lines = mutable_file.read_last_lines(15, buffer_length=10)

    assert len(lines) == 15
    # first five lines have 9 + 1(\n) symbols (a-lines)
    assert all(len(lines[i]) == 10 for i in range(5))
    # other lines have 10 + 1(\n) symbols (b-lines)
    assert all(len(lines[i]) == 11 for i in range(5, len(lines)))


def test_mutable_file_readline_file_not_exists(tmp_path: Path):
    tmp_file = tmp_path / "file.txt"

    mutable_file = MutableFile(tmp_file)

    assert mutable_file.readline() == ""
    assert mutable_file.readline() == ""  # always None


def test_mutable_file_readline_empty_file(tmp_path: Path):
    tmp_file = tmp_path / "file.txt"
    tmp_file.touch()

    mutable_file = MutableFile(tmp_file)

    assert mutable_file.readline() == ""
    assert mutable_file.readline() == ""  # always None


def test_mutable_file_readline_simple(tmp_path: Path):
    tmp_file = tmp_path / "file.txt"
    tmp_file.write_text("hello\nworld\n")

    # file not updated
    mutable_file = MutableFile(tmp_file)
    assert mutable_file.readline() == "hello\n"
    assert mutable_file.readline() == "world\n"
    assert mutable_file.readline() == ""

    test_line = "hello\n"
    newline = "\n"
    write_to_end(tmp_file, test_line + newline)
    assert mutable_file.readline() == test_line
    assert mutable_file.readline() == newline
    assert mutable_file.readline() == ""


def test_mutable_file_readline_without_newline(tmp_path: Path):
    tmp_file = tmp_path / "file.txt"
    tmp_file.write_text("hello\nworld\n")

    # file not updated
    mutable_file = MutableFile(tmp_file)
    assert mutable_file.readline() == "hello\n"
    assert mutable_file.readline() == "world\n"
    assert mutable_file.readline() == ""

    test_line = "hello"
    write_to_end(tmp_file, test_line)
    assert mutable_file.readline() == ""

    newline = "\n"
    write_to_end(tmp_file, newline)
    assert mutable_file.readline() == test_line + newline
    assert mutable_file.readline() == ""


@pytest.mark.skipif(sys.platform.startswith("win"), reason="can't unlink an open file")
def test_mutable_file_continue_read_after_remove(tmp_path: Path):
    tmp_file = tmp_path / "file.txt"
    tmp_file.write_text("hello\nworld\n")

    # file not updated
    mutable_file = MutableFile(tmp_file)
    assert mutable_file.readline() == "hello\n"
    assert mutable_file.readline() == "world\n"
    assert mutable_file.readline() == ""

    test_line = "hello\n"
    write_to_end(tmp_file, test_line)
    assert mutable_file.readline() == test_line

    tmp_file.unlink()
    assert mutable_file.readline() == ""

    tmp_file.write_text("second\nfile\n")
    assert mutable_file.readline() == "second\n"
    assert mutable_file.readline() == "file\n"
    assert mutable_file.readline() == ""
