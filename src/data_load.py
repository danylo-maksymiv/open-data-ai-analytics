import os
import urllib.request
import ssl
import sys


def download_data(url, save_path):
    print(f"Починаємо завантаження даних з {url}...")

    # Твій правильний рядок (створюємо папки, якщо їх нема)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    # 1. Одягаємо "маску" звичайного браузера Chrome на Windows
    req = urllib.request.Request(
        url,
        headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
    )

    # 2. Вимикаємо строгу перевірку сертифікатів (державні сайти часто мають з цим проблеми)
    context = ssl._create_unverified_context()

    try:
        # 3. Використовуємо urlopen замість urlretrieve.
        # Додаємо timeout=20 (чекаємо максимум 20 секунд, а не 5 хвилин!)
        with urllib.request.urlopen(req, timeout=20, context=context) as response:
            with open(save_path, 'wb') as out_file:
                out_file.write(response.read())

        print(f"Дані успішно завантажено та збережено у {save_path}")

    except Exception as e:
        # Якщо сталася помилка (таймаут або блок), скрипт красиво зупиниться і покаже причину
        print(f"❌ Помилка завантаження: {e}")
        sys.exit(1)


if __name__ == "__main__":
    DATA_URL = "https://data.gov.ua/dataset/0d28afe4-25cc-41a8-a8c9-5e07ef0c55d3/resource/a2c589de-ec79-481c-9203-e54a826906d8/revision/92993/download"
    LOCAL_PATH = "../data/raw/kontrolno-perevirochna-robota.csv"

    download_data(DATA_URL, LOCAL_PATH)