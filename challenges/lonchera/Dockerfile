FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py ./
COPY items.json ./
COPY templates ./templates
COPY static ./static

RUN useradd --create-home challenge
USER challenge

EXPOSE 8080
CMD ["python", "app.py"]
