# Аналіз ефективності перевірок у сфері боротьби з відмиванням доходів в Україні

## Мета: 

Дослідити результативність документальних перевірок у різних регіонах України та виявити залежність між типом перевірки (планова чи позапланова) і кількістю виявлених матеріалів з ознаками кримінальних правопорушень.

## Джерело:
[Показники контрольно-перевірочної роботи Департаменту боротьби з відмиванням доходів](https://data.gov.ua/)

Завантажити дані можна за [посиланням](https://data.gov.ua/dataset/0d28afe4-25cc-41a8-a8c9-5e07ef0c55d3/resource/a2c589de-ec79-481c-9203-e54a826906d8/revision/92993/download)
## Гіпотези дослідження:
Гіпотеза 1: Позапланові перевірки є більш результативними та частіше призводять до виявлення кримінальних правопорушень, оскільки зазвичай проводяться на основі конкретних підозр.

Гіпотеза 2: Існує значна диспропорція між регіонами: абсолютна більшість виявлених фінансових правопорушень концентрується у кількох найбільш економічно активних областях (наприклад, Київська, Львівська).

Питання: Який загальний відсоток (конверсія) документальних перевірок закінчується складанням матеріалів для кримінальних справ, і які регіони є "лідерами" за цим показником?

## Архітектура та структура проєкту

Проєкт побудовано на базі мікросервісної архітектури за допомогою **Docker Compose**. Кожен етап аналізу ізольований у власному контейнері.

```text
.
├── compose.yaml                # Головний оркестратор сервісів
├── .env                        # Файл конфігурації
├── data_load/                  # Сервіс №1: Завантаження та ініціалізація БД
├── data_quality/               # Сервіс №2: Очищення даних
├── data_research/              # Сервіс №3: Перевірка гіпотез (JSON-генератор)
├── visualization/              # Сервіс №4: Генерація графіків (Jupyter nbconvert)
└── web/                        # Сервіс №5: Flask веб-інтерфейс
```

## Опис сервісів (Docker Containers)

- `kpr-data-load`: Завантажує сирий CSV-файл з порталу відкритих даних (обходячи блокування через кастомні User-Agent) та конвертує його в реляційну базу даних SQLite.
- `kpr-quality`: Читає дані з БД, видаляє дублікати та пропуски, генерує звіт якості `quality_report.json` та повертає чисті дані в БД.
- `kpr-research`: Аналізує чисті дані, перевіряє дві основні гіпотези, рахує конверсію перевірок і формує `research_report.json`.
- `kpr-visualization`: Працює у фоновому режимі (headless jupyter). Генерує графіки (`.png`) та створює маніфест для фронтенду.
- `kpr-web`: Web-сервер на базі Flask. Чекає завершення всіх аналітичних сервісів і рендерить фінальний дашборд.

## Мережа та Порти

- Внутрішня мережа: `analytics-net` (bridge)
- Зовнішній порт: `5050`
- Внутрішній порт Flask: `5000`
- Доступ до веб-інтерфейсу: http://localhost:5050

## Інструкція із запуску (Docker Workspace)

Для локального запуску всього конвеєра необхідний встановлений Docker та Docker Desktop.

1. Клонуйте репозиторій та перейдіть у його корінь.
2. Виконайте команду збірки та запуску:

```bash
docker compose up --build
```

3. Дочекайтеся завершення роботи аналітичних сервісів (у логах з'явиться `kpr-web | * Running on all addresses`).
4. Відкрийте браузер за адресою http://localhost:5050.

---
 
## Крок 1. Відкрити AWS CloudShell
 
1. Перейти на [console.aws.amazon.com](https://console.aws.amazon.com) та увійти в обліковий запис.
2. У правому верхньому куті натиснути іконку **CloudShell** (`>_`).
3. Дочекатися запуску оболонки (перший раз — близько хвилини).
4. Переконатися, що Terraform встановлений:
```bash
terraform -v
```
 
Якщо команда не знайдена — встановити:
 
```bash
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://rpm.releases.hashicorp.com/AmazonLinux/hashicorp.repo
sudo yum install terraform -y
```
 
---
 
## Крок 2. Підготовка
 
Згенерувати SSH-ключ для доступу до VM:
 
```bash
ssh-keygen -t rsa -b 4096 -f ~/.ssh/lab_key -N ""
```
 
Клонувати репозиторій:
 
```bash
git clone https://github.com/danylo-maksymiv/open-data-ai-analytics.git
cd open-data-ai-analytics/infra/terraform
```
 
Задати змінну з публічним ключем:
 
```bash
export TF_VAR_ssh_public_key="$(cat ~/.ssh/lab_key.pub)"
```
 
---
 
## Крок 3. Виконати `terraform apply`
 
Ініціалізувати провайдер:
 
```bash
terraform init
```
 
Перевірити конфігурацію і переглянути план:
 
```bash
terraform fmt
terraform validate
terraform plan
```
 
Застосувати — створити інфраструктуру:
 
```bash
terraform apply -auto-approve
```
 
Після завершення Terraform виведе:
 
```
Apply complete! Resources: X added, 0 changed, 0 destroyed.
 
Outputs:
web_public_ip = "XX.XX.XX.XX"
website_url   = "http://XX.XX.XX.XX:5050"
```
 
> **Увага:** після створення VM потрібно зачекати **5–10 хвилин**, поки cloud-init завершить збірку Docker-образів і запустить контейнери.
 
---
 
## Крок 4. Перевірити результат
 
Відкрити веб-інтерфейс у браузері за адресою з output:
 
```
http://XX.XX.XX.XX:5050
```
 
Або перевірити HTTP-відповідь прямо з CloudShell:
 
```bash
curl http://$(terraform output -raw web_public_ip):5050/health
# Очікувана відповідь: {"status": "ok"}
```
 
Щоб перевірити стан контейнерів через SSH:
 
```bash
ssh -i ~/.ssh/lab_key ubuntu@$(terraform output -raw web_public_ip)
docker ps
# або переглянути логи cloud-init:
sudo tail -100 /var/log/cloud-init-output.log
```
 
---
 
## Крок 5. Виконати `terraform destroy`
 
**Після демонстрації обов'язково видалити всі ресурси**, щоб не витрачати кредит AWS:
 
```bash
terraform destroy -auto-approve
```
 
Переконатися, що EC2-інстанс зупинений у AWS Console: **EC2 → Instances**.
 
---
 
## Опис Terraform-ресурсів
 
| Ресурс | Призначення |
|--------|-------------|
| `aws_vpc` | Ізольована мережа для інфраструктури |
| `aws_subnet` | Підмережа з публічними IP |
| `aws_internet_gateway` | Доступ до інтернету |
| `aws_route_table` | Таблиця маршрутизації |
| `aws_security_group` | Дозволяє порти 22 (SSH) та 5050 (web) |
| `aws_key_pair` | SSH-ключ для доступу до VM |
| `aws_instance` | EC2 Ubuntu VM (t3.micro) з cloud-init |
| `aws_eip` | Статичний публічний IP |
 

# Моніторинг проєкту KPR Analytics — Prometheus + Grafana

> Стек моніторингу розгорнуто разом із основним Docker-проєктом через `compose.yaml`. Метрики збираються з хост-системи та Docker-контейнерів, візуалізуються в Grafana.

---

## Архітектура моніторингу

```
┌─────────────────────────────────────────────────────┐
│                  Docker Compose                      │
│                                                      │
│  node-exporter (:9100) ──┐                          │
│                           ├──► Prometheus (:9090)   │
│  cAdvisor      (:8080) ──┘         │                │
│                                    ▼                │
│                           Grafana (:3000)           │
└─────────────────────────────────────────────────────┘
```

---

## Як розгортається моніторинг

Моніторинг запускається автоматично разом з основним проєктом однією командою:

```bash
docker compose up -d
```

Prometheus зчитує конфігурацію з файлу `monitoring/prometheus/prometheus.yml`, який монтується як volume. Grafana стартує з попередньо налаштованими змінними оточення (логін/пароль).

Перевірити, що всі сервіси моніторингу запущені:

```bash
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

---

## Сервіси, що збирають метрики

| Сервіс | Образ | Призначення |
|--------|-------|-------------|
| **node-exporter** | `prom/node-exporter:latest` | Метрики хост-системи: CPU, RAM, диск, мережа |
| **cAdvisor** | `gcr.io/cadvisor/cadvisor:v0.49.0` | Метрики Docker-контейнерів: ресурси кожного контейнера |
| **prometheus** | `prom/prometheus:latest` | Збирає (scrape) метрики кожні 15 секунд, зберігає time-series |
| **grafana** | `grafana/grafana:latest` | Візуалізація метрик у вигляді дашбордів |

### Конфігурація Prometheus (`monitoring/prometheus/prometheus.yml`)

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']

  - job_name: 'cadvisor'
    static_configs:
      - targets: ['cadvisor:8080']
```

---

## Відкриті порти

| Порт | Сервіс | URL | Призначення |
|------|--------|-----|-------------|
| **5050** | web (Flask) | `http://HOST:5050` | Основний веб-інтерфейс застосунку |
| **9090** | Prometheus | `http://HOST:9090` | Веб-інтерфейс Prometheus, перегляд метрик і targets |
| **3000** | Grafana | `http://HOST:3000` | Дашборди моніторингу |
| **9100** | node-exporter | `http://HOST:9100/metrics` | Raw метрики хост-системи |
| **8080** | cAdvisor | `http://HOST:8080` | Raw метрики контейнерів |

---

## Як відкрити Grafana

1. Відкрити браузер і перейти за адресою:
   ```
   http://<PUBLIC_IP>:3000
   ```
2. Ввести облікові дані за замовчуванням:
   - **Логін:** `admin`
   - **Пароль:** `admin`
3. Після першого входу Grafana запропонує змінити пароль (можна пропустити).

### Налаштування джерела даних Prometheus

Якщо джерело даних не налаштоване автоматично:

1. **Connections → Data sources → Add new data source**
2. Вибрати **Prometheus**
3. URL: `http://prometheus:9090`
4. Натиснути **Save & test** — має з'явитися повідомлення `Successfully queried the Prometheus API`

### Перевірка targets у Prometheus

Перейти на:
```
http://<PUBLIC_IP>:9090/targets
```
Всі три targets (`cadvisor`, `node-exporter`, `prometheus`) мають мати статус **UP**.

---

## Панелі (дашборди), що створено

### 1. Node Exporter Full (імпортований, ID: 1860)

Готовий дашборд зі спільноти Grafana для моніторингу хост-системи через node-exporter. Містить:

- **Quick CPU / Mem / Disk** — зведені gauge-індикатори: завантаження CPU, RAM, I/O
- **CPU Basic** — графік завантаження процесора (Busy System, Busy User, Idle тощо)
- **Memory Basic** — використання оперативної пам'яті (Used, Cache+Buffer, Free, Swap)
- **Network Traffic Basic** — швидкість мережевого трафіку (вхідний/вихідний)
- **Disk Space Used Basic** — відсоток використання дискового простору

### 2. Власний дашборд (ручне створення)

Створено кастомний дашборд з трьома панелями на базі метрик node-exporter:

| Панель | Метрика | Тип |
|--------|---------|-----|
| **Завантаження ЦП у %** | `100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)` | Time series |
| **Використання оперативки** | `node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes` | Time series |
| **Disk I/O** | `rate(node_disk_io_time_seconds_total[5m])` | Time series |

---

## Структура файлів моніторингу

```
monitoring/
└── prometheus/
    └── prometheus.yml    # Конфігурація Prometheus (targets та інтервал збору)
```
