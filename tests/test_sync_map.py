

def test_sync_map(complete_sync_map):
    sync_map = complete_sync_map
    text1, text2, text3 = 'p001.xhtml', 'p002.xhtml', 'p003.xhtml'

    assert len(sync_map) == 3
    for text in [text1, text2, text3]:
        assert text in sync_map

        for fragment_id in sync_map[text]:
            fragment_map = sync_map[text][fragment_id]
            assert 'audio_file' in fragment_map
            assert 'begin_time' in fragment_map
            assert 'end_time' in fragment_map

            assert fragment_map['begin_time'] < fragment_map['end_time']
