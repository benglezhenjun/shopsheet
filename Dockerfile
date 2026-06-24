FROM python:3.12-slim

WORKDIR /app

ENV PYTHONPATH=/app/src

COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY examples ./examples

EXPOSE 8000

CMD ["uvicorn", "shopsheet.api:app", "--host", "0.0.0.0", "--port", "8000"]
