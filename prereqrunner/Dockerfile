FROM python:3.9-slim
RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && apt-get purge -y --auto-remove \
    && rm -rf /var/lib/apt/lists/*

# see https://pythonspeed.com/articles/alpine-docker-python/ for the reason we don't use alpine
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install --use-deprecated=legacy-resolver -r requirements.txt

COPY ./ ./prereqrunner/

ENV PYTHONPATH=$PYTHONPATH:.

# -u disables stdout buffering https://stackoverflow.com/questions/107705/disable-output-buffering
CMD [ "python3", "-u", "/app/prereqrunner/main.py"]