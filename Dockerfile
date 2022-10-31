FROM python:3
ENV PYTHONUNBUFFERED=1

LABEL maintainer="jonghwanhyeon93@gmail.com" \
      org.opencontainers.image.source="https://github.com/jonghwanhyeon/gpugpu-exporter"

WORKDIR /code
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

EXPOSE 9700
CMD ["python3", "run.py"]