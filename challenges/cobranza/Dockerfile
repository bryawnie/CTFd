FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py ./

RUN useradd --create-home challenge
USER challenge

EXPOSE 8080
# Un solo worker: el registro de sesiones (sid -> BD) vive en memoria del
# proceso, asi que con mas de uno los jugadores perderian su progreso.
CMD ["gunicorn", "--workers", "1", "--bind", "0.0.0.0:8080", "app:app"]
