from graphviz import Digraph
import os
from pathlib import Path
import time

def now():
    return round(time.time() * 1000)

def save_file_content(file, content):
    with open(file, "w", encoding="utf-8") as f:
        f.write(content)

def get_file_content(file):
    with open(file, "r", encoding="utf-8") as f:
        t = f.read()
    return t

def get_root(d, f):
    path = Path(os.path.abspath(__file__))
    return os.path.abspath(os.path.join(path.parent.parent, d, f))

def get_db(f):
    path = Path(os.path.abspath(__file__))
    return os.path.abspath(os.path.join(path.parent.parent, "db", f))

def get_map(f):
    path = Path(os.path.abspath(__file__))
    return os.path.abspath(os.path.join(path.parent.parent, "map", f))

def get_images(f):
    path = Path(os.path.abspath(__file__))
    return os.path.abspath(os.path.join(path.parent.parent, "images", f))

def is_int(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False