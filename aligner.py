import os.path
import subprocess
import time

from aeneas.audiofilemfcc import AudioFileMFCC
from aeneas.language import Language
from aeneas.synthesizer import Synthesizer
from aeneas.textfile import TextFile, TextFileFormat
from aeneas.executetask import ExecuteTask
from aeneas.exacttiming import TimeValue
from aeneas.tree import Tree
import numpy as np

import algorithms


def align(text_path, audio_path, output_dir):
    tmp_dir = os.path.join(output_dir, 'tmp')
    os.makedirs(tmp_dir, exist_ok=True)

    # get MFCC sequence of recorded audio
    audio_wav_path = os.path.join(tmp_dir, 'audio.wav')
    subprocess.run(['ffmpeg', '-i', audio_path, audio_wav_path])

    rec_mfcc_seq = AudioFileMFCC(audio_wav_path).all_mfcc.T[:, 1:]

    # get MFCC sequence and anchors of synthesized audio
    synthesizer = Synthesizer()
    parse_parameters = {
        'is_text_unparsed_id_regex': 'f[0-9]+'
    }
    textfile = TextFile(text_path, file_format=TextFileFormat.UNPARSED, parameters=parse_parameters)
    textfile.set_language(Language.ENG)
    text_wav_path = os.path.join(tmp_dir, 'text.wav')
    anchors,_,_ = synthesizer.synthesize(textfile, text_wav_path)

    synth_mfcc_seq = AudioFileMFCC(text_wav_path).all_mfcc.T[:, 1:]

    #dist_func = lambda x,y: np.linalg.norm(x-y)
    dist_func = norm_dist


    print(rec_mfcc_seq.shape, synth_mfcc_seq.shape)
    anchor_indices = np.array([int(x[0] / TimeValue('0.040')) for x in anchors])
    print(anchor_indices)

    # start = time.time()
    # distance, path = algorithms.FastDTW(synth_mfcc_seq, rec_mfcc_seq, dist_func, 100)
    # # print(path, distance)
    # print(time.time() - start)

    # synth_path_indices = np.array([x[0] for x in path])
    # rec_path_indices = np.array([x[1] for x in path])
    # begin_indices = np.searchsorted(synth_path_indices, anchor_indices)
    # boundary_indices = rec_path_indices[begin_indices]
    # rec_anchors = boundary_indices * 0.040
    # for t, r in zip(anchors, rec_anchors):
    #     print(t, r)

    start = time.time()
    distance, path = algorithms.simpleNWTW(synth_mfcc_seq, rec_mfcc_seq, dist_func, 1.9)
    # print(path, distance)
    print(time.time() - start)

    # print(anchores)
    
    synth_path_indices = np.array([x[0] for x in path])
    rec_path_indices = np.array([x[1] for x in path])
    begin_indices = np.searchsorted(synth_path_indices, anchor_indices, side='right')
    boundary_indices = rec_path_indices[begin_indices]
    rec_anchors = boundary_indices * 0.040
    for t, r in zip(anchors, rec_anchors):
        print(t, r)

    # execute_task = ExecuteTask()
    # sync_root = Tree()
    # execute_task._adjust_boundaries(boundary_indices, textfile, rec_mfcc_seq, sync_root)


def norm_dist(x, y):
    return 1 - x.T @ y / np.linalg.norm(x) / np.linalg.norm(y)


# align('resources/typee/01.xhtml', 'resources/typee/typee_01_melville_64kb.mp3', 'resources/typee')
align('resources/shake/p001.xhtml', 'resources/shake/p001.mp3', 'resources/shake/')