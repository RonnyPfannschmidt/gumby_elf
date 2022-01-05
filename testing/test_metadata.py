from gumby_elf import _metadata as metadata


WHEEL_DEFAULT_META = """\
Wheel-Version: 1.0
Generator: gumby_elf pre alpha
Root-Is-Purelib: true
Tag: py3-none-any\
"""


def test_entrypoints():
    class FakeMetadata:
        gui_scripts = scripts = {}
        entrypoints = {
            "pytest": {
                "a": "b",
            }
        }

    metadata_11 = metadata.entrypoints_txt(FakeMetadata)
    assert metadata_11 == b"[pytest]\na = b\n\n"


def test_wheelinfo():
    wi = metadata.get_wheel_info()
    print(wi)
    assert wi.decode() == WHEEL_DEFAULT_META
