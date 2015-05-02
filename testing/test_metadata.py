from gumby_elf import metadata

def test_entrypoints():
    ep = metadata.EntryPoints.from_spec_dict({
        'pytest': {
            'a': 'b',
        }
    })

    metadata_11 = ep.to_11_metadata()
    assert metadata_11 == (
        '[pytest]\n'
        'a = b'
    )

