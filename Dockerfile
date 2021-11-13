FROM python:3.9-slim

RUN apt update -q \
    && apt install --no-install-recommends -yq espeak \
    libespeak-dev \
    ffmpeg
RUN apt install -yq gcc

RUN pip install numpy==1.21.2
RUN pip install pytest==6.2.5

WORKDIR /afaligner
COPY src src
COPY tests tests
COPY LICENSE MANIFEST.in README.md setup.py ./

RUN pip install .

WORKDIR /
ENTRYPOINT []
CMD ["bash"]