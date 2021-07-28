FROM python:3.8-slim-buster

WORKDIR /app

COPY app /app

RUN python3 setup.py install
RUN pip3 freeze

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
