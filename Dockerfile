FROM python:3.11

WORKDIR /app
COPY . /app

# ffmpeg/ffprobe power the enhanced player's multi-audio/subtitle track
# probing and subtitle extraction (feature merged in from telestream-bot).
# The bot still runs fine without them - those features just silently
# turn themselves off (see ENABLE_SUBTITLES / ENABLE_TRACK_PROBE).
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "-m", "WOODStream"]
