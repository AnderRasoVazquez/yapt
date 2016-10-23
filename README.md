# yapt [Yaourt APT]

yapt implements an installation menu interface around `apt search` command like `yaourt` does in Arch Linux.

**Normal apt command**
![](img/apt.png)

**yapt command**
![](img/yapt.png)

# Usage

```
usage: yapt [-h] [-y] [-d] [-n] pkg

positional arguments:
  pkg              the package to search.

optional arguments:
  -h, --help       show this help message and exit
  -y, --noconfirm  don't ask for confirmation.
  -d, --debug      debug mode (don't execute command).
  -n, --nocolor    no colored output.

```

## Dependencies

+ python3

## Installation


