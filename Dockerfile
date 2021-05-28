FROM python:3.8-slim
COPY exporter.py requirements.txt /
RUN pip install -r requirements.txt
ENTRYPOINT ["python", "exporter.py"]
