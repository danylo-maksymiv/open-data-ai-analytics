FROM python:3.11-slim

WORKDIR /app

# Встановлюємо системні залежності для matplotlib
RUN apt-get update && apt-get install -y --no-install-recommends \
    libfreetype6-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо твій ноутбук
COPY visualization.ipynb .

# Запускаємо ноутбук у фоновому режимі
CMD ["jupyter", "nbconvert", "--to", "notebook", "--execute", "visualization.ipynb", "--output", "executed_visualization.ipynb"]