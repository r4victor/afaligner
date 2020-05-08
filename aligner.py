from datetime import timedelta
import os.path
import subprocess
import time
import logging

from aeneas.audiofilemfcc import AudioFileMFCC
from aeneas.language import Language
from aeneas.synthesizer import Synthesizer
from aeneas.textfile import TextFile, TextFileFormat
from aeneas.exacttiming import TimeValue
from aeneas.runtimeconfiguration import RuntimeConfiguration
import numpy as np

from alignment_algorithms import c_DTWBD, FastDTWBD, c_FastDTWBD


def align(audio_dir, text_dir, output_dir):
    tmp_dir = os.path.join(output_dir, 'tmp')
    os.makedirs(tmp_dir, exist_ok=True)
    
    text_paths = (os.path.join(text_dir, f) for f in sorted(os.listdir(text_dir)))
    audio_paths = (os.path.join(audio_dir, f) for f in sorted(os.listdir(audio_dir)))

    text_to_audio_map = create_map(text_paths, audio_paths, tmp_dir)

    return text_to_audio_map

    # create_smil(text_to_audio_map, output_dir)


def create_map(text_paths, audio_paths, tmp_dir):
    """
    This function builds a mapping between a series of text files and a series of audio files
    representing the same work. Mapping is built by synthesizing text and then aligning it with the recorded audio.
    
    The main features of this algorithm is that:
    1) It can handle structural differences in the beginning and in the end of files.
    2) It does not require one-to-one correspondance between text and audio files (i.e. the splitting can be done differently).
    
    Alignment details:
    Synthesized and recorded audio are represented as sequences of MFCC frames.
    These sequences are aligned using variation of DTW algorithm.
    In contrast to the classic DTW, this algorithms can be used
    to align sequences with structural differences in the beginning or in the end.
    This is done by mapping frames of extra content to the single (first or last) frame of the opposite sequence.
    
    Steps to build a mapping:
    1) Synthesize text file and produce a list of anchors.
    Each anchor represents the start of the corresponding text fragment in a synthesized audio.
    2) Get sequences of MFCC frames of synthesized and recorded audio.
    3) Get their warping path by calling the alignment algorithm.
    4) Check whether the extra content is found, calculate mapping boundaries.
    5) Map anchors inside the boundaries to the recorded MFCC sequence using warping path from step 3.
    6) Start all over again considering:
    If there is an extra content in the end of synthesized sequence, align it with next audio file.
    If there is an extra content in the end of recorded sequence, align it with next text file.
    If none of the above, align next text and audio files.
    """
    skip_penalty = 0.75

    synthesizer = Synthesizer()
    parse_parameters = {'is_text_unparsed_id_regex': 'f[0-9]+'}
    
    text_to_audio_map = {}
    process_next_text = True
    process_next_audio = True

    while True:
        if process_next_text:
            try:
                text_path = next(text_paths)
            except StopIteration:
                break

            text_name = get_name_from_path(text_path)
            textfile = TextFile(text_path, file_format=TextFileFormat.UNPARSED, parameters=parse_parameters)
            textfile.set_language(Language.ENG)
            text_wav_path = os.path.join(tmp_dir, f'{drop_extension(text_name)}_text.wav')
            text_to_audio_map[text_name] = {}

            # Produce synthesized audio, get anchors
            anchors,_,_ = synthesizer.synthesize(textfile, text_wav_path)
            
            # Get fragments, convert anchors timings to the frames indicies
            fragments = [a[1] for a in anchors]
            anchors = np.array([int(a[0] / TimeValue('0.040')) for a in anchors])

            # MFCC frames sequence memory layout is a n x l 2D array,
            # where n - number of frames and l - number of MFFCs
            # i.e it is c-contiguous, but after dropping the first coefficient it siezes to be c-contiguous.
            # Should decide whether to make a copy or to work around the first coefficient.
            text_mfcc_sequence = np.ascontiguousarray(
                AudioFileMFCC(text_wav_path).all_mfcc.T[:, 1:]
            )
            
        if process_next_audio:
            try:
                audio_path = next(audio_paths)
            except StopIteration:
                break

            audio_name = get_name_from_path(audio_path)
            audio_wav_path = os.path.join(tmp_dir, f'{drop_extension(audio_name)}_audio.wav')
            subprocess.run(['ffmpeg', '-n', '-i', audio_path, audio_wav_path])

            audio_mfcc_sequence = np.ascontiguousarray(
                AudioFileMFCC(audio_wav_path).all_mfcc.T[:, 1:]
            )
            
            # Keep track to calculate frames timings
            audio_start_frame = 0
        
        n = len(text_mfcc_sequence)
        m = len(audio_mfcc_sequence)

        _, path = c_FastDTWBD(text_mfcc_sequence, audio_mfcc_sequence, skip_penalty, radius=200)
        
        if len(path) == 0:
            print(
                f'No match between {text_name} and {audio_name}. '
                f'Alignment is terminated. '
                f'Adjust skip_penalty or input files.'
            )
            return {}
        
        # Project path to the text and audio sequences
        text_path_frames = path[:,0]
        audio_path_frames = path[:,1]
        
        last_matched_audio_frame = audio_path_frames[-1]

        # Find first and last matched frames
        first_matched_text_frame = text_path_frames[0]
        last_matched_text_frame = text_path_frames[-1]

        # Map only those fragments that intersect matched frames
        anchors_boundary_indices = np.searchsorted(
            anchors, [first_matched_text_frame, last_matched_text_frame]
        )
        map_anchors_from = max(anchors_boundary_indices[0] - 1, 0)
        map_anchors_to = anchors_boundary_indices[1]
        anchors_to_map = anchors[map_anchors_from:map_anchors_to]
        fragments_to_map = fragments[map_anchors_from:map_anchors_to]

        # Get anchors indicies in the path projection to the text sequence
        text_path_anchor_indices = np.searchsorted(text_path_frames, anchors_to_map)
        
        # Get anchors' frames in audio sequence, calculate their timings
        anchors_matched_frames = audio_path_frames[text_path_anchor_indices]
        anchors_timings = (anchors_matched_frames + audio_start_frame) * 0.040
        
        # Map fragment_ids to timings, update mapping of the current text file
        fragment_map = {f: (audio_name, t) for f, t in zip(fragments_to_map, anchors_timings)}
        text_to_audio_map[text_name].update(fragment_map)
        
        # Decide whether to process next file or to align the tail of the current one

        if map_anchors_to == len(anchors):
            # Process next text if no fragments are left
            process_next_text = True
        else:
            # Otherwise align tail of the current text
            process_next_text = False
            text_mfcc_sequence = text_mfcc_sequence[last_matched_text_frame:]
            fragments = fragments[map_anchors_to:]
            anchors = anchors[map_anchors_to:] - last_matched_text_frame
            
        if last_matched_audio_frame == m - 1 or not process_next_text:
            # Process next audio if there are no unmatched audio frames in the tail
            # or there are more text fragments to map, i.e.
            # we choose to process next audio if we cannot decide.
            # This strategy is correct if there are no extra fragments in the end.
            process_next_audio = True
        else:
            # Otherwise align tail of the current audio
            process_next_audio = False
            audio_mfcc_sequence = audio_mfcc_sequence[last_matched_audio_frame:]
            audio_start_frame += last_matched_audio_frame
    
    return text_to_audio_map


def get_name_from_path(path):
    return os.path.split(path)[1]


def drop_extension(path):
    return os.path.splitext(path)[0]


def create_smil(text_to_audio_map, output_dir):
    pass


def show_mapping(text_to_audio_map):
    for text, fragment_map in text_to_audio_map.items():
        print(text)
        for fragment, val in fragment_map.items():
            print(fragment, f'{val[0]} {timedelta(seconds=int(val[1]))}')


if __name__ == '__main__':
    # show_mapping(align('resources/tests/text_audio_head/audio', 'resources/tests/text_audio_head/text', 'resources/tests/text_audio_head/'))
    # show_mapping(align('resources/tests/audio_head/audio', 'resources/tests/audio_head/text', 'resources/tests/audio_head/'))
    # show_mapping(align('resources/tests/3_to_3/audio', 'resources/tests/3_to_3/text', 'resources/tests/3_to_3/'))
    import time
    n = time.time()
    show_mapping(align('resources/duty/audio', 'resources/duty/text', 'resources/duty/'))
    print(time.time() - n)
