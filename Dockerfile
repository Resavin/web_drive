FROM python:3.11


WORKDIR /web_drive

COPY requirements.txt ./

# RUN --mount=type=cache,target=/root/.cache/pip \
    # pip3 install -r requirements.txt
RUN pip3 install -r requirements.txt

COPY .env ./
COPY app ./app

WORKDIR /web_drive/data

EXPOSE 8000

CMD ["python", "../app/run.py"]
# CMD ["sh", "-c", "tail -f /dev/null"]
