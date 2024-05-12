ARG PYTHON_VERSION=3.12

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
COPY --from=mwader/static-ffmpeg:6.1 /ffmpeg /usr/local/bin/ 
COPY --from=mwader/static-ffmpeg:6.1 /ffprobe /usr/local/bin/
COPY --from=build-venv /opt/venv /opt/venv
COPY . .

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV VIRTUAL_ENV=/opt/venv
ENV PATH=$VIRTUAL_ENV/bin:$PATH
CMD ["python", "-m", "vk_extract_audio_bot"]
