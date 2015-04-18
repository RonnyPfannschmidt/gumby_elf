"""bootstrap script"""

import sys
import subprocess
import json
import types


with open('package.json') as fp:
    data = json.load(fp)


package = data['python package']


requires = [
    k if v == 'latest' else '%s=%s' % (k, v)
    for k, v in package['dependencies'].items()
]
subprocess.check_call(['pip', 'install', '-q', '-U'] + requires)


mod = types.ModuleType(str(package['package']))
sys.modules[str(package['package'])] = mod
mod.__path__ = ['src']
execfile('src/__init__.py', mod.__dict__)


from gumby_elf.cli import main
main(['develop'])
