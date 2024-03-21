# FROM python:3
# # FROM python:3.10-alpine # apt-get: not found

# CMD ["/bin/bash"]
FROM python:3.11-alpine

WORKDIR /work
COPY requirements.txt ./
RUN pip install -r requirements.txt

WORKDIR /app

COPY ./ .

CMD ["python", "sample_bolt.py"]
# CMD ["python", "main.py", "--m", "abc@gmailcom"]