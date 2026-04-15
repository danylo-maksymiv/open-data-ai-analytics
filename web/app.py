import os
import json
import sqlite3
import time
from flask import Flask, render_template, send_from_directory, jsonify

app = Flask(__name__)

DB_PATH      = os.getenv('DB_PATH',      '/db/analytics.db')
REPORTS_DIR  = os.getenv('REPORTS_DIR',  '/reports')
PLOTS_DIR    = os.getenv('PLOTS_DIR',    '/plots')


def wait_for_files(retries=30, delay=2):
    """Чекаємо поки всі сервіси завершать роботу"""
    required = [
        DB_PATH,
        os.path.join(REPORTS_DIR, 'quality_report.json'),
        os.path.join(REPORTS_DIR, 'research_report.json'),
        os.path.join(PLOTS_DIR, 'manifest.json'),  # <--- Змінили тут
    ]
    for attempt in range(retries):
        missing = [f for f in required if not os.path.exists(f)]
        if not missing:
            return True
        print(f"⏳ [{attempt+1}/{retries}] Очікуємо файли: {missing}")
        time.sleep(delay)
    return False


def read_json(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        return {"error": str(e)}


def get_db_data():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT * FROM inspections ORDER BY \"Кількість складених матеріалів з ознаками кримінальних правопорушень всього\" DESC").fetchall()
        conn.close()
        return [dict(r) for r in rows]
    except Exception as e:
        return []


@app.route('/')
def index():
    quality  = read_json(os.path.join(REPORTS_DIR, 'quality_report.json'))
    research = read_json(os.path.join(REPORTS_DIR, 'research_report.json'))
    data     = get_db_data()

    # Список графіків
    plots = []
    manifest_path = os.path.join(PLOTS_DIR, 'manifest.json')
    if os.path.exists(manifest_path):
        manifest = read_json(manifest_path)
        plots = manifest.get('plots', [])

    return render_template('index.html',
                           quality=quality,
                           research=research,
                           data=data,
                           plots=plots)


@app.route('/plots/<filename>')
def serve_plot(filename):
    return send_from_directory(PLOTS_DIR, filename)


@app.route('/api/data')
def api_data():
    return jsonify(get_db_data())


@app.route('/api/quality')
def api_quality():
    return jsonify(read_json(os.path.join(REPORTS_DIR, 'quality_report.json')))


@app.route('/api/research')
def api_research():
    return jsonify(read_json(os.path.join(REPORTS_DIR, 'research_report.json')))


@app.route('/health')
def health():
    return jsonify({"status": "ok"})


if __name__ == '__main__':
    print("=" * 55)
    print("  ВЕБ-СЕРВІС (web)")
    print("=" * 55)
    print("⏳ Перевіряємо наявність усіх даних...")
    if not wait_for_files():
        print("⚠️  Деякі файли відсутні, але стартуємо все одно...")
    print("🌐 Запускаємо Flask на 0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)
