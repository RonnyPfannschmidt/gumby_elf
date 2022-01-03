"""
bootstrap script

will do a devleop install of gumby elf
"""

import sys
import types


mod = types.ModuleType("gumby_elf")
sys.modules[mod.__name__] = mod
mod.__path__ = ["src"]
with open("src/__init__.py") as fp:
    code = fp.read()
code = compile(code, "src/__init__.py", "exec")
exec(code, mod.__dict__)

from gumby_elf.build_backend import *
