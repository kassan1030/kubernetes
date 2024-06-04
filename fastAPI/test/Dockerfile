FROM python:3.10-slim
USER root

RUN apt-get update
RUN apt-get install -y vim less
RUN pip install --upgrade pip

RUN pip install --no-cache-dir fastapi uvicorn

COPY app app

EXPOSE 8000

CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8000"]