import os
import sys
import runpy

root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(root, "src"))

runpy.run_path(os.path.join(root, "src", "nuevo_bot_tickets.py"), run_name="__main__")
