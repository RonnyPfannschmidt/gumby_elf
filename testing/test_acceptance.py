from __future__ import print_function
import pytest



from gumby_elf.cli import main



@pytest.mark.parametrize(
    'command, results', [
        (['build_sdist'], ()),
        (['build_wheel'], ()),
        (['build_wheel', '--develop'], ()),
        (['build_eggs'], ()),
    ])
def test_builds_commands(command, results, tmpdir):
    main(['--root', tmpdir.strpath] + command)
