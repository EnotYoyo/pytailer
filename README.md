# PyTAILer

PyTAILer is very simple implementation of the unix shell utility `tail`.

```python
from pytailer import fail_tail

with fail_tail("some_file.txt", lines=10) as tail:
    for line in tail:  # be careful: infinite loop!
        print(line)
```