FROM python:3.11-slim
COPY app.py /app/
WORKDIR /app
RUN pip install fastapi uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]

