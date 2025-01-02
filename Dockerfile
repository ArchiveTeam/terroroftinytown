FROM python:3.12-alpine
RUN apk add git
WORKDIR /usr/src
COPY requirements-tracker.txt .
RUN pip3 install -r requirements-tracker.txt
COPY . .
ENTRYPOINT ["python3", "-m", "terroroftinytown.tracker", "tracker_docker.conf"]
