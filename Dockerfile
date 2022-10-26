FROM python:3.9-slim

RUN apt update -q \
    && apt install --no-install-recommends -yq espeak \
    libespeak-dev \
    ffmpeg
RUN apt install -yq gcc

RUN pip install numpy==1.23.4
RUN pip install pytest==7.1.3

WORKDIR /afaligner
COPY src src
COPY tests tests
COPY LICENSE MANIFEST.in README.md setup.py ./

RUN pip install .

WORKDIR /
ENTRYPOINT []
CMD ["bash"]
