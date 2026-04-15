import os
import sqlite3
import pandas as pd
import json
import sys


def perform_research():
    # 1. Читаємо змінні середовища (шляхи в Docker)
    db_path = os.getenv('DB_PATH', '/db/analytics.db')
    report_path = os.getenv('REPORT_PATH', '/reports/research_report.json')

    print(f"Завантаження даних для дослідження з БД {db_path}...\n")
    try:
        conn = sqlite3.connect(db_path)
        df = pd.read_sql("SELECT * FROM inspections", conn)
        conn.close()
    except Exception as e:
        print(f"❌ Помилка читання з БД: {e}")
        sys.exit(1)

    # Назви колонок (залишаємо як у тебе)
    col_total_checks = 'Взято участь у проведенні документальних перевірок відповідно до ПКУ всього'
    col_planned_checks = ' у т.ч. планових'
    col_unplanned_checks = 'у т.ч. позапланових'
    col_total_crimes = 'Кількість складених матеріалів з ознаками кримінальних правопорушень всього'
    col_planned_crimes = ' у т.ч. за результатами  планових переврок'
    col_unplanned_crimes = ' у т.ч. за результатами позапланових перевірок'

    # === ГІПОТЕЗА 1: Планові vs Позапланові перевірки ===
    total_planned = int(df[col_planned_checks].sum())
    total_unplanned = int(df[col_unplanned_checks].sum())
    crimes_planned = int(df[col_planned_crimes].sum())
    crimes_unplanned = int(df[col_unplanned_crimes].sum())

    conv_planned = round((crimes_planned / total_planned * 100), 1) if total_planned > 0 else 0.0
    conv_unplanned = round((crimes_unplanned / total_unplanned * 100), 1) if total_unplanned > 0 else 0.0

    h1_confirmed = bool(conv_unplanned > conv_planned)
    h1_conclusion = "Позапланові перевірки ефективніші" if h1_confirmed else "Планові перевірки ефективніші"

    print(f"Планові перевірки: всього {total_planned}, порушень {crimes_planned} ({conv_planned}%)")
    print(f"Позапланові перевірки: всього {total_unplanned}, порушень {crimes_unplanned} ({conv_unplanned}%)")

    # === ГІПОТЕЗА 2: Диспропорція між регіонами ===
    total_crimes_all = int(df[col_total_crimes].sum())
    top_regions_abs = df.nlargest(3, col_total_crimes)[['Назва регіону', col_total_crimes]]

    top3_list = []
    for _, row in top_regions_abs.iterrows():
        top3_list.append({"region": str(row['Назва регіону']), "crimes": int(row[col_total_crimes])})

    top_3_sum = sum(item['crimes'] for item in top3_list)
    top3_share = round((top_3_sum / total_crimes_all * 100), 1) if total_crimes_all > 0 else 0.0

    print(f"Загальна кількість порушень: {total_crimes_all}")
    print(f"=> Топ-3 регіони генерують {top3_share}% усіх виявлених правопорушень.\n")

    # === БАЗОВА СТАТИСТИКА (Для карток зверху сайту) ===
    regions_count = int(df['Назва регіону'].nunique())
    total_checks = int(df[col_total_checks].sum())
    overall_conversion = round((total_crimes_all / total_checks * 100), 1) if total_checks > 0 else 0.0

    # === ТОП-5 ЗА КОНВЕРСІЄЮ ===
    df['Конверсія (%)'] = df.apply(
        lambda row: (row[col_total_crimes] / row[col_total_checks] * 100) if row[col_total_checks] > 0 else 0, axis=1
    )
    top_conversion = df[df[col_total_crimes] > 0].nlargest(5, 'Конверсія (%)')

    top5_list = []
    for _, row in top_conversion.iterrows():
        top5_list.append({
            "region": str(row['Назва регіону']),
            "conversion_pct": round(float(row['Конверсія (%)']), 1)
        })

    # === 2. ЗБИРАЄМО JSON-ЗВІТ ===
    # Структура чітко підігнана під index.html з папки web
    report = {
        "basic_stats": {
            "regions_count": regions_count,
            "total_checks": total_checks,
            "total_planned": total_planned,
            "total_unplanned": total_unplanned,
            "total_crimes": total_crimes_all,
            "overall_conversion_pct": overall_conversion
        },
        "hypothesis_1": {
            "title": "Планові vs Позапланові перевірки",
            "confirmed": h1_confirmed,
            "conclusion": h1_conclusion,
            "planned_checks": total_planned,
            "planned_crimes": crimes_planned,
            "planned_conv_pct": conv_planned,
            "unplanned_checks": total_unplanned,
            "unplanned_crimes": crimes_unplanned,
            "unplanned_conv_pct": conv_unplanned
        },
        "hypothesis_2": {
            "title": "Диспропорція між регіонами (Топ-3)",
            "confirmed": True,
            "conclusion": f"Топ-3 регіони генерують {top3_share}% порушень",
            "top3_regions": top3_list,
            "top3_share_pct": top3_share
        },
        "top5_by_conversion": top5_list
    }

    # === 3. ЗБЕРЕЖЕННЯ ===
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"✅ Дослідження завершено. JSON-звіт збережено у {report_path}")


if __name__ == "__main__":
    perform_research()