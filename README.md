# LemonParser

Parse `.cdf` file of [lemonlime](https://github.com/Project-LemonLime/Project_LemonLime), and generate uoj-format `problem.conf`!

Features:
- Support subtask & subtask dependence.
- Support special judge.
- Cross-platform.

Usage:
```
main.py [-h] [-S] [--task [TASK]] filename

positional arguments:
  filename       Lemon work path

options:
  -h, --help     show this help message and exit
  -S, --silent   Silent mode
  -A, --attach   Attach statement
  -Z, --zip      Auto create zipfile
  --task [TASK]  Parse specific task (* for all)
```