"""
Load global configurations, if they exist in a config.ini file
"""

import configparser
from os import path
from .execute import check_clang, check_llvmlink

CONFIG = configparser.ConfigParser()
CONFIG.read(path.join(path.dirname(__file__), "..", "config.ini"))

CLANG = CONFIG.get("toolchain", "clang", fallback="clang")
LLVMLINK = CONFIG.get("toolchain", "llvmlink", fallback="llvm-link")


def check_config():
    """ Check config variables are valid for exection """
    check_clang(CLANG)
    check_llvmlink(LLVMLINK)