# FROM python:3
# # FROM python:3.10-alpine # apt-get: not found

FROM python:3.11-alpine

WORKDIR /work
COPY requirements.txt ./
RUN pip install -r requirements.txt

WORKDIR /app

COPY ./ .

CMD ["python", "-B", "sample_bolt.py"]