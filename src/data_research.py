import pandas as pd


def perform_research(file_path):
    print(f"Завантаження даних для дослідження з {file_path}...\n")
    try:
        df = pd.read_csv(file_path, sep=';')

        col_total_checks = 'Взято участь у проведенні документальних перевірок відповідно до ПКУ всього'
        col_planned_checks = ' у т.ч. планових'
        col_unplanned_checks = 'у т.ч. позапланових'

        col_total_crimes = 'Кількість складених матеріалів з ознаками кримінальних правопорушень всього'
        col_planned_crimes = ' у т.ч. за результатами  планових переврок'
        col_unplanned_crimes = ' у т.ч. за результатами позапланових перевірок'

        print("=== ГІПОТЕЗА 1: Планові vs Позапланові перевірки ===")
        total_planned = df[col_planned_checks].sum()
        total_unplanned = df[col_unplanned_checks].sum()
        crimes_planned = df[col_planned_crimes].sum()
        crimes_unplanned = df[col_unplanned_crimes].sum()

        conv_planned = (crimes_planned / total_planned * 100) if total_planned > 0 else 0
        conv_unplanned = (crimes_unplanned / total_unplanned * 100) if total_unplanned > 0 else 0

        print(
            f"Планові перевірки: всього {total_planned}, виявлено порушень {crimes_planned} (Конверсія: {conv_planned:.1f}%)")
        print(
            f"Позапланові перевірки: всього {total_unplanned}, виявлено порушень {crimes_unplanned} (Конверсія: {conv_unplanned:.1f}%)")
        if conv_unplanned > conv_planned:
            print("=> Висновок: Гіпотеза 1 ПІДТВЕРДЖЕНА. Позапланові перевірки ефективніші.\n")
        else:
            print("=> Висновок: Гіпотеза 1 СПРОСТОВАНА.\n")

        print("=== ГІПОТЕЗА 2: Диспропорція між регіонами ===")
        total_crimes_all = df[col_total_crimes].sum()
        top_regions_abs = df.nlargest(3, col_total_crimes)[['Назва регіону', col_total_crimes]]

        display_top_regions = top_regions_abs.rename(columns={col_total_crimes: 'К-сть порушень'})
        top_3_sum = top_regions_abs[col_total_crimes].sum()

        print(f"Загальна кількість порушень по Україні: {total_crimes_all}")
        print("Топ-3 регіони за кількістю:")
        print(display_top_regions.to_string(index=False))
        print(f"=> Топ-3 регіони генерують {(top_3_sum / total_crimes_all * 100):.1f}% усіх виявлених правопорушень.\n")

        print("=== ПИТАННЯ: Загальний відсоток (конверсія) перевірок ===")
        overall_conversion = (total_crimes_all / df[col_total_checks].sum()) * 100
        print(f"Загальна конверсія перевірок у кримінальні справи по Україні: {overall_conversion:.1f}%\n")

        df['Конверсія (%)'] = df.apply(
            lambda row: (row[col_total_crimes] / row[col_total_checks] * 100) if row[col_total_checks] > 0 else 0,
            axis=1
        )

        top_conversion = df[df[col_total_crimes] > 0].nlargest(5, 'Конверсія (%)')[
            ['Назва регіону', 'Конверсія (%)', col_total_checks, col_total_crimes]]

        display_top_conversion = top_conversion.rename(columns={
            col_total_checks: 'Всього перевірок',
            col_total_crimes: 'Знайдено порушень'
        })
        display_top_conversion['Конверсія (%)'] = display_top_conversion['Конверсія (%)'].round(1)

        print("Регіони-лідери за % успішності перевірок (конверсією):")
        print(display_top_conversion.to_string(index=False))

    except Exception as e:
        print(f"Сталася помилка при аналізі даних: {e}")


if __name__ == "__main__":
    INPUT = "../data/raw/kontrolno-perevirochna-robota.csv"
    perform_research(INPUT)