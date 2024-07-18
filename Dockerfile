FROM python:3.11


WORKDIR /web_drive

COPY requirements.txt ./

# RUN --mount=type=cache,target=/root/.cache/pip \
    # pip3 install -r requirements.txt
RUN pip3 install -r requirements.txt

COPY .env ./

# COPY app ./app

WORKDIR /web_drive/data

EXPOSE 8000

ENV PYTHONPATH=/web_drive
# CMD ["pytest", "/web_drive/app"]
CMD ["python", "/web_drive/app/run.py"]
# CMD ["uvicorn", "app:app", "--host", "$APP_HOST", "--port", "$APP_PORT"]
# CMD ["sh", "-c", "tail -f /dev/null"]
