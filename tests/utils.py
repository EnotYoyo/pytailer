from pathlib import Path
from typing import AnyStr


def write_to_end(file: Path, line: AnyStr):
    with file.open("a") as io:
        io.write(line)
