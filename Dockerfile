ARG PYTHON_VERSION=3.10

FROM python:${PYTHON_VERSION} as build-venv
WORKDIR /poetry
COPY pyproject.toml poetry.lock /
RUN pip install --upgrade pip \
    && pip install poetry \
    && poetry self add poetry-plugin-export \
    && poetry export --only main -o requirements.txt --without-hashes \
    && python -m venv /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

FROM python:${PYTHON_VERSION}-slim AS runtime-image
WORKDIR /app
RUN mkdir .db \
    && mkdir .temp \
    && mkdir .temp/audios \
    && mkdir .temp/videos
COPY --from=mwader/static-ffmpeg:6.1 /ffmpeg /usr/local/bin/ 
COPY --from=mwader/static-ffmpeg:6.1 /ffprobe /usr/local/bin/
COPY --from=build-venv /opt/venv /opt/venv
COPY /vk_extract_audio_from_video_bot .

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV VIRTUAL_ENV=/opt/venv
ENV PATH=$VIRTUAL_ENV/bin:$PATH
CMD ["python", "-m", "main"]
