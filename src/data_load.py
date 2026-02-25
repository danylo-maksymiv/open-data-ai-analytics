import os
import urllib.request


def download_data(url, save_path):
    print(f"Починаємо завантаження даних з {url}...")

    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    urllib.request.urlretrieve(url, save_path)

    print(f"Дані успішно завантажено та збережено у {save_path}")


if __name__ == "__main__":
    DATA_URL = "https://data.gov.ua/dataset/0d28afe4-25cc-41a8-a8c9-5e07ef0c55d3/resource/a2c589de-ec79-481c-9203-e54a826906d8/revision/92993/download"

    LOCAL_PATH = "../data/raw/kontrolno-perevirochna-robota.csv"

    download_data(DATA_URL, LOCAL_PATH)