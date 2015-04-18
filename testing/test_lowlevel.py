from gumby_elf.lowlevel import create_script


def test_makescript(tmpdir):
    create_script(
        bin=tmpdir.strpath,
        name='test',
        entrypoint='foo:bar',
    )


