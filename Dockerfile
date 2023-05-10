FROM python:3.8

ADD main.py .

RUN pip install sentinelsat pandas matplotlib

VOLUME ["/data/"]

CMD ["python", "./main.py"]
