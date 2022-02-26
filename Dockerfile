FROM python:3
MAINTAINER IvanAlfonso
 
RUN pip install flask \ 
 && pip install kubernetes \ 
 && pip install paho-mqtt

COPY adapter-engine /home/
CMD [ "python", "/home/server.py" ]
EXPOSE 8000
