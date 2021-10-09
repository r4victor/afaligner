# afaligner

## Overview

<b>afaligner</b> is a Python library for automatic text and audio synchronization (a.k.a forced aligner). You give it a list of text files and a list of audio files that contain the narrated text, and it produces a mapping between text fragments and the corresponding audio fragments.


<b>afaligner</b> is used in the [syncabook](https://github.com/r4victor/syncabook) command-line tool to produce EPUB3 with Media Overlays ebooks and has been developed for this specific purpose. If you want to create an ebook with synchronized text and audio, consider using [syncabook](https://github.com/r4victor/syncabook) instead of using <b>afaligner</b> directly.

<b>afaligner</b> works by synthesizing text and then aligning synthesized and recorded audio using a variation of the [DTW](https://en.wikipedia.org/wiki/Dynamic_time_warping) (Dynamic Time Warping) algorithm. The main features of the algorithm are:

* It can handle structural differences in the beginning and in the end of files, which is often the case with audiobooks (e.g. disclaimers).

* It finds an approximation to an optimal warping path in linear time and space using the FastDTW approach. This and the fact that the algorithm is implemented in C make it pretty fast compared to other forced aligners.

* It can, with varying success, align differently split text and audio. 

<b>afaligner</b> was inspired by [aeneas](https://github.com/readbeyond/aeneas) and works in a similiar way. It uses <b>aeneas</b> as a dependency for text synthesis and MFCC extraction.

## Supported platforms

<b>afaligner</b> works on 64-bit Mac OS and Linux. Windows is not currently supported (you may try to use a VM).

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
   pip install numpy
   ```

4. Install <b>afaligner</b>:
   ```
   pip install afaligner
   ```

Or if you want to modify the <b>afaligner</b>'s source code:

4. Get the repository:

   ```
   git clone https://github.com/r4victor/afaligner/ && cd afaligner
   ```

5. Install <b>afaligner</b> in editable mode:
   ```
   pip install -e .
   ```

## Running tests

1. Install `pytest`:
   ```
   pip install pytest
   ```

2. Run tests:
   ```
   python -m pytest tests/
   ```

## Installation via Docker

Installing all the <b>afaligner</b>'s dependencies can be tedious, so the library comes with Dockerfile. You can use it to build a Debian-based Docker image that contains <b>afaligner</b> itself and all its dependencies. Alternatively, you can use Dockerfile as a reference to install <b>afaligner</b> on your machine.

Installation via Docker:

1. Get the repository:

   ```
   git clone https://github.com/r4victor/afaligner/ && cd afaligner
   ```

2. Build an image:
   ```
   docker build -t afaligner .
   ```

3. Now you can run the container like so:
   ```
   docker run -ti afaligner
   ```
   It enters bash. You can run Python and `import afaligner`. To do something useful, you may need to mount your code that uses <b>afaligner</b> as a volume.

## Usage

<b>afaligner</b> provides only one function called `align()` that takes a text directory, an audio directory, and a set of output parameters and returns a sync map (a mapping from text fragments to their time positions in audio files). If the output directory is specified, it also writes the result in the JSON or SMIL format to that directory. The call may look like this:

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

and `sync_map` has the following structure:

```python
{
    "p001.xhtml": {
        "f001": {
            "audio_file": "p001.mp3",
            "begin_time": "0:00:00.000",
            "end_time": "0:00:02.600",
        },
        "f002": {
            "audio_file": "p001.mp3",
            "begin_time": "0:00:02.600",
            "end_time": "0:00:05.880",
        },
        # ...
    },
    "p002.xhtml": {
        "f016": {
            "audio_file": "p002.mp3",
            "begin_time": "0:00:00.000",
            "end_time": "0:00:03.040",
        }
        # ...
    },
}
```

For more details, please refer to docstrings.

## Troubleshooting

`pip install afaligner` may not work on macOS if it tries to compile a [universal library](https://developer.apple.com/documentation/apple-silicon/building-a-universal-macos-binary). This seems to be because `aeneas` complies only on x86_64. I got an error when using Python 3.9. The following command fixes it:

```
ARCHFLAGS="-arch x86_64" pip install afaligner
```