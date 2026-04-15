import os
import urllib.request
import ssl
import sys
import sqlite3
import pandas as pd


def download_data(url, save_path):
    # Якщо файл уже примонтований через volume або скачаний — пропускаємо
    if os.path.exists(save_path):
        print(f"Файл {save_path} вже існує локально. Завантаження пропущено.")
        return

    print(f"Починаємо завантаження даних з {url}...")
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    req = urllib.request.Request(
        url,
        headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
    )

    context = ssl._create_unverified_context()

    try:
        with urllib.request.urlopen(req, timeout=20, context=context) as response:
            with open(save_path, 'wb') as out_file:
                out_file.write(response.read())
        print(f"Дані успішно завантажено та збережено у {save_path}")

    except Exception as e:
        print(f"❌ Помилка завантаження: {e}")
        sys.exit(1)


if __name__ == "__main__":
    DATA_URL = "https://data.gov.ua/dataset/0d28afe4-25cc-41a8-a8c9-5e07ef0c55d3/resource/a2c589de-ec79-481c-9203-e54a826906d8/revision/92993/download"

    # Читаємо шляхи зі змінних середовища Docker (якщо їх нема - ставимо дефолтні)
    CSV_PATH = os.environ.get("CSV_PATH", "/tmp/kontrolno-perevirochna-robota.csv")
    DB_PATH = os.environ.get("DB_PATH", "/db/analytics.db")

    # 1. Завантажуємо файл (якщо потрібно)
    download_data(DATA_URL, CSV_PATH)

    # 2. Читаємо CSV через Pandas
    print(f"Читаємо дані з {CSV_PATH}...")
    try:
        df = pd.read_csv(CSV_PATH, sep=';')
    except Exception as e:
        print(f"❌ Помилка читання CSV: {e}")
        sys.exit(1)

    # 3. Зберігаємо в SQLite
    print(f"Зберігаємо дані в базу {DB_PATH}...")
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)  # Гарантуємо, що папка існує

    try:
        conn = sqlite3.connect(DB_PATH)
        # Заливаємо всю таблицю в БД (назвемо її 'inspections')
        df.to_sql('inspections', conn, if_exists='replace', index=False)
        conn.close()
        print("✅ Дані успішно імпортовано в базу даних SQLite!")
    except Exception as e:
        print(f"❌ Помилка роботи з БД: {e}")
        sys.exit(1)