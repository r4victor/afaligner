from datetime import timedelta
import os

from afaligner import align

from . import RESOURCES_DIR


def test_complete_sync(complete_sync_map):
    """
    Three audio files perfectly map to three text files.
    """
    pass


def test_text_extra_head():
    """
    Text starts with extra lines. Ensure that those are skipped.
    """
    sync_map = align(
        os.path.join(RESOURCES_DIR, 'shakespeare/text_extra_head/'),
        os.path.join(RESOURCES_DIR, 'shakespeare/audio/'),
        times_as_timedelta=True
    )
    text = 'p001.xhtml'
    last_extra_line_id = 'f0005'
    audio_starts_before = timedelta(seconds=3)
    
    # The last extra line should not be mapped at all or mapped before audio starts
    assert (
        last_extra_line_id not in sync_map[text] or
        sync_map[text][last_extra_line_id]['end_time'] < audio_starts_before
    )


    


