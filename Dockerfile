# dockerfile -> blueprint for building docker image 
# docker image -> template for running container (like class)
# docker container -> instance of image 

# specify dockerhub baseImage 
FROM python:3.8

ADD main.py .

RUN pip install sentinelsat pandas

CMD ["python", "./main.py"]

