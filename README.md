# LemonParser

Parse `.cdf` file of [lemonlime](https://github.com/Project-LemonLime/Project_LemonLime), and generate uoj-format `problem.conf`!

Features:
- Support subtask & subtask dependence.
- Support special judge.
- Cross-platform.
- Convert pdf statement to markdown using LLMs.

Usage:
```
usage: main.py [-h] [-S] [-D] [-E] [-H] [-Z] [--task [TASK]] [--noip-checker]
               [--parse-pdf]
               filename

Parse Lemonlime conf files(.cdf)

positional arguments:
  filename           Lemon work path

options:
  -h, --help         show this help message and exit
  -S, --silent       Silent mode
  -D, --attach-down  Attach statement and samples
  -E, --editorial    Attach editorial
  -H, --enable-hack  Enable hack(both std and validator are required)
  -Z, --zip          Auto create zipfile
  --task [TASK]      Parse specific task (* for all)
  --noip-checker     Use noip-style checker instead of `wcmp`
  --parse-pdf        [Experimental] use gemini 2.5 flash to generate markdown
                     version of statement from pdf, you need to set the
                     OPENROUTER_API_KEY environment variable
```
