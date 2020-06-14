FROM python:3.8

RUN wget https://github.com/mattgreen/watchexec/releases/download/1.8.6/watchexec-1.8.6-x86_64-unknown-linux-gnu.tar.gz
RUN tar -xvf watchexec-1.8.6-x86_64-unknown-linux-gnu.tar.gz watchexec-1.8.6-x86_64-unknown-linux-gnu
RUN mv watchexec-1.8.6-x86_64-unknown-linux-gnu/watchexec /usr/local/bin

WORKDIR /work
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
