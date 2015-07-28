from __future__ import print_function
import pytest
from subprocess import check_call


@pytest.fixture
def package(tmpdir):
    return tmpdir


@pytest.fixture
def call_virtualenv(tmpdir):
    check_call(['virtualenv', tmpdir.join('venv').strpath])

    def call_virtualenv(name, *args):
        print(name, args)
        check_call([tmpdir.join('venv/bin').join(name).strpath] + list(args))

    call_virtualenv('pip', 'install', 'setuptools_scm')
    call_virtualenv('python', 'lone_elf.py')
    return call_virtualenv


def test_wheel(package, call_virtualenv):
    call_virtualenv('gumby', 'build_wheel')
