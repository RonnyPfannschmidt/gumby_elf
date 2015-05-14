"""
bootstrap script

will do a devleop install of gumby elf
"""

import sys
import subprocess
import types

if '--plain' not in sys.argv:
    import email
    with open('METADATA.in') as fp:
        message = email.message_from_file(fp)

    requires = message.get_all('Requires-Dist')
    requires = [x for x in requires if ';' not in x]
    subprocess.check_call(['pip', 'install', '-q', '-U'] + requires)

mod = types.ModuleType('gumby_elf')
sys.modules[mod.__name__] = mod
mod.__path__ = ['src']
with open('src/__init__.py') as fp:
    code = fp.read()
code = compile(code, 'src/__init__.py', 'exec')
exec(code, mod.__dict__)


from gumby_elf.cli import main
main(['develop'])
