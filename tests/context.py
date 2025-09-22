import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

print("sys.path:", sys.path)
print("cwd:", os.getcwd())

from pychanasync import Channel, chanselect
