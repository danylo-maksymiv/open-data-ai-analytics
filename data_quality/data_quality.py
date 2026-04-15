import os
import sqlite3
import pandas as pd
import json
import sys


def check_and_clean_data():
    # 1. Читаємо змінні середовища (шляхи в Docker)
    db_path = os.getenv('DB_PATH', '/db/analytics.db')
    report_path = os.getenv('REPORT_PATH', '/reports/quality_report.json')

    print(f"Підключення до бази {db_path}...")
    try:
        conn = sqlite3.connect(db_path)
        df = pd.read_sql("SELECT * FROM inspections", conn)
    except Exception as e:
        print(f"❌ Помилка читання з БД: {e}")
        sys.exit(1)

    print(f"Початковий розмір таблиці: {df.shape[0]} рядків, {df.shape[1]} колонок.")

    # 2. Збираємо статистику для JSON-звіту
    missing_count = int(df.isnull().sum().sum())
    duplicates_count = int(df.duplicated().sum())

    # Розділяємо колонки на текстові та числові
    num_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    text_cols = df.select_dtypes(exclude=['int64', 'float64']).columns.tolist()

    # Збираємо інформацію по діапазонах для числових колонок
    ranges = {}
    for col in num_cols:
        ranges[col] = {
            "min": float(df[col].min()) if not df[col].empty else 0,
            "max": float(df[col].max()) if not df[col].empty else 0,
            "negative_values": int((df[col] < 0).sum())
        }

    # 3. Очищення даних
    if missing_count > 0:
        df = df.dropna()
        print(f"Видалено {missing_count} пустих клітинок.")

    if duplicates_count > 0:
        df = df.drop_duplicates()
        print(f"Видалено {duplicates_count} дублікатів.")

    # Визначаємо статус для вебу
    if missing_count == 0 and duplicates_count == 0:
        overall_status = "ДАНІ ЯКІСНІ"
    else:
        overall_status = "ОЧИЩЕНО ВІД СМІТТЯ"

    print(f"Розмір таблиці після очищення: {df.shape[0]} рядків.")

    # 4. Формуємо JSON-звіт (структура чітко під index.html)
    report = {
        "summary": {"overall_status": overall_status},
        "shape": {"rows": len(df), "columns": len(df.columns)},
        "missing_values": {"total": missing_count},
        "duplicates": {"count": duplicates_count},
        "type_check": {
            "numeric_columns": num_cols,
            "text_columns": text_cols
        },
        "value_ranges": ranges
    }

    # Зберігаємо JSON
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"✅ JSON-звіт збережено у: {report_path}")

    # 5. Перезаписуємо таблицю в БД уже чистими даними
    try:
        df.to_sql('inspections', conn, if_exists='replace', index=False)
        print("✅ Очищені дані успішно збережено в БД!")
    except Exception as e:
        print(f"❌ Помилка запису в БД: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    check_and_clean_data()