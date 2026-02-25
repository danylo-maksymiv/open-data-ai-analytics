import pandas as pd
import os


def check_and_clean_data(input_path, output_path):
    print(f"Завантаження даних з {input_path}...\n")
    try:
        df = pd.read_csv(input_path, sep=';')
        print(f"Початковий розмір таблиці: {df.shape[0]} рядків, {df.shape[1]} колонок.")

        missing_count = df.isnull().sum().sum()
        if missing_count > 0:
            df = df.dropna()
            print(f"Загалом пустих клітинок було: {missing_count}")
        else:
            print("Пустих значень не знайдено.")

        duplicates_count = df.duplicated().sum()
        if duplicates_count > 0:
            df = df.drop_duplicates()
            print(f"Видалено дублікатів: {duplicates_count}")
        else:
            print("Дублікатів не знайдено.")

        print(f"\nРозмір таблиці після очищення: {df.shape[0]} рядків.")

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, sep=';', index=False)
        print(f"Очищені дані успішно збережено у: {output_path}")

    except FileNotFoundError:
        print(f"Помилка: Файл {input_path} не знайдено. Перевір шлях до файлу.")


if __name__ == "__main__":
    INPUT_FILE = "../data/raw/kontrolno-perevirochna-robota.csv"
    OUTPUT_FILE = "../data/processed/cleaned_data.csv"

    check_and_clean_data(INPUT_FILE, OUTPUT_FILE)