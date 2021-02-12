# afaligner

## Overview

<b>afaligner</b> is a Python library for automatic text and audio synchronization. It's a forced aligner that works by synthesizing text and then aligning synthesized and recorded audio using a variation of [DTW](https://en.wikipedia.org/wiki/Dynamic_time_warping) (Dynamic Time Warping) algorithm.

<b>afaligner</b> is used in a [syncabook](https://github.com/r4victor/syncabook) tool for synchronization of narrated audio with text – to produce EPUB3 with Media Overlays ebooks – and has been developed for this specific purpose. If you want to create an ebook with synchronized text and audio, please refer to [syncabook](https://github.com/r4victor/syncabook).

The main features of the alignment algorithm behind <b>afaligner</b> are:

* It can handle structural differences in the beginning and in the end of files which is often the case with audiobooks (e.g. disclaimers).

* It finds an approximation to an optimal warping path in linear time and space using FastDTW approach which, combined with the fact that The alignment algorithm itself is written in C, makes it pretty fast compared to other forced aligners.

* It can, with varying success, align differently splitted text and audio. 

<b>afaligner</b> was inspired by [aeneas](https://github.com/readbeyond/aeneas) and works in a similiar way. It uses <b>aeneas</b> as a dependency for text synthesis and MFCC extraction.

## Supported platforms

<b>afaligner</b> works on 64-bit Mac OS and Linux. Windows is not currently supported.

## Requirements

* Python (>= 3.6)
* FFmpeg
* eSpeak
* Python packages: `aeneas`, `numpy`, `jinja2`

## Installation

1. Install [Python](https://www.python.org/) (>= 3.6)

2. Install [FFmpeg](https://www.ffmpeg.org/) and [eSpeak](http://espeak.sourceforge.net/)

3. Install <b>numpy</b>:
```
$ pip install numpy
```

4. Install <b>afaligner</b>:
```
$ pip install afaligner
```

Or if you want to modify <b>afaligner</b>'s code:
1. Get <b>afaligner</b>:
```
$ git clone https://github.com/r4victor/afaligner/ && cd afaligner
```

2. Install <b>afaligner</b> in editable mode:
```
$ pip install -e .
```

## Running tests

1. Install `pytest`:

```
$ pip install pytest
```

2. Run tests:

```
$ python -m pytest tests/
```

## Usage

<b>afaligner</b> is designed to be used as a library. If you want to produce an ebook with synchronized text and audio or just to perform a synchronization, you may want to take a look at a command line tool called [syncabook](https://github.com/r4victor/syncabook).

<b>afaligner</b> provides only one function called `align` which takes a text directory, an audio directory and a set of output parameters and returns a sync map (a mapping from text fragments to their time positions in audio files) and, if requested, writes the result to disk. The call may look like this:

```python
from afaligner import align


sync_map = align(
    'ebooks/demoebook/text/',
    'ebooks/demoebook/audio/',
    output_dir='ebooks/demoebook/smil/',
    output_format='smil',
    sync_map_text_path_prefix='../text/',
    sync_map_audio_path_prefix='../audio/'
)
```

For more details, please refer to docstrings.

