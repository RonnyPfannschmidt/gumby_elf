"""bootstrap script"""

import os
import sys
import subprocess
import json


with open('package.json') as fp:
    data = json.load(fp)

package = data['pythonPackage']
requires = [
    k if v == 'latest' else '%s=%s' % (k, v)
    for k, v in package['dependencies'].items()
]
subprocess.call(['pip', 'install'] + requires)



sys.path.insert(0, 'src')

from gumby_elf import main
main(['develop'])
