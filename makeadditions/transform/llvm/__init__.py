"""
Import all modules from this directory
Needed for automatic transformer registration
"""

from os.path import dirname, basename, isfile, join
from glob import glob

__all__ = [basename(f)[:-3] for f in glob(join(dirname(__file__), "*.py"))
           if isfile(f) and not f.endswith("__init__.py")]
