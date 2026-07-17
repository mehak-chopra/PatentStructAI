"python -m tests.test_base_recognizer (in molnextr env)"

import sys
from pathlib import Path

print("Current working directory:")
print(Path.cwd())

print()

print("sys.path:")
for p in sys.path:
    print(p)

print()

from chemistry.recognizers.base import BaseRecognizer

print("Import successful!")

try:
    BaseRecognizer()
except TypeError as e:
    print(e)