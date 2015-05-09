"""bootstrap script"""

import sys
import subprocess
import json
import types





if '--plain' not in sys.argv:
    from src.config import GumbyLowlevelIniSpecification

    with open('gumby_elf.ll.ini') as fp:
        spec = GumbyLowlevelIniSpecification(fp)

    requires = spec.get_requires()
    subprocess.check_call(['pip', 'install', '-q', '-U'] + requires)

mod = types.ModuleType('gumby_elf')
sys.modules[mod.__name__] = mod
mod.__path__ = ['src']
execfile('src/__init__.py', mod.__dict__)


from gumby_elf.cli import main
main(['develop'])
