from gumby_elf import metadata


WHEEL_DEFAULT_META = """\
Wheel-Version: 1.0
Generator: gumby_elf pre alpha
Root-Is-Purelib: true
Tag: py27-none-any
Tag: py3-none-any\
"""


def test_entrypoints():
    ep = metadata.EntryPoints.from_spec_dict(
        {
            "pytest": {
                "a": "b",
            }
        }
    )

    metadata_11 = ep.to_11_metadata()
    assert metadata_11 == ("[pytest]\n" "a = b")


def test_wheelinfo():
    wi = metadata.WheelInfo.default()
    print(wi)
    assert str(wi) == WHEEL_DEFAULT_META
