"""
Exploration: inspect the structure of one raw record before cleaning.
"""

import json
from pathlib import Path

raw_file = Path("data/raw/UDC.jsonl")

# Read only the first line of the file (one publication)
with open(raw_file, encoding="utf-8") as f:
    first_line = f.readline()

# json.loads turns the JSON text into a Python dictionary
work = json.loads(first_line)

# Print it with indentation so the nested structure is readable
print(json.dumps(work, indent=2, ensure_ascii=False))
