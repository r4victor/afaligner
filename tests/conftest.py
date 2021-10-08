import os

import pytest

from afaligner import align

from . import RESOURCES_DIR


@pytest.fixture(scope='session')
def complete_sync_map():
    """
    Three audio files perfectly map to three text files.
    """
    return align(
        os.path.join(RESOURCES_DIR, 'shakespeare/text_complete/'),
        os.path.join(RESOURCES_DIR, 'shakespeare/audio/'),
        times_as_timedelta=True
    )