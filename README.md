# PyTAILer

PyTAILer is very simple implementation of the unix shell utility `tail`.

```python
from pytailer import fail_tail

with fail_tail("some_file.txt", lines=10) as tail:
    for line in tail:  # be careful: infinite loop!
        print(line)
```

Of course, you can use async version:

```python
import asyncio

from pytailer import async_fail_tail


async def main():
    with async_fail_tail("some_file.txt", lines=10) as tail:
        async for line in tail:  # be careful: infinite loop!
            print(line)


asyncio.run(main())  # python 3.7+ 
```
