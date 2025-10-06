<div align="center">

  <h1>AI Dashboards & Logs Monitoring</h1>

  <h3>Автоматизированный мониторинг инфраструктуры с AI</h3>
  
  [![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python)](https://python.org)
  [![Docker](https://img.shields.io/badge/Docker--compose-grey?style=for-the-badge&logo=docker)](https://docker.com)
  <img alt="OpenAI" src="https://img.shields.io/badge/OpenAI-GPT--4-blue?style=for-the-badge&logo=openai&logoColor=white" />
</div>

> [!NOTE]\
>  <b>Проект выполнен в рамках хакатона “МТС Engineer Hack — DevOps”</b>

<div align="center">

  <img src="docs/banner_mts_hack.png" alt="МТС Engineer Hack - DevOps — проект AI Monitoring" />
</div>

## 🛠️ Технологический стек / Tech Stack

<div style="display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 15px;"> <img alt="Python" src="https://img.shields.io/badge/-Python-ffbc03?&logo=Python&style=for-the-badge" /> <a href="https://www.docker.com/"><img alt="Docker" src="https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white&style=for-the-badge"></a> <a href="https://prometheus.io/"><img alt="Prometheus" src="https://img.shields.io/badge/Prometheus-E6522C?logo=prometheus&logoColor=white&style=for-the-badge"></a> <a href="https://grafana.com/"><img alt="Grafana" src="https://img.shields.io/badge/Grafana-F46800?logo=grafana&logoColor=white&style=for-the-badge"></a> <a href="https://redis.io/"><img alt="Redis" src="https://img.shields.io/badge/Redis-DC382D?logo=redis&logoColor=white&style=for-the-badge"></a> <a href="https://www.postgresql.org/"><img alt="PostgreSQL" src="https://img.shields.io/badge/PostgreSQL-4169E1?logo=postgresql&logoColor=white&style=for-the-badge"></a> <a href="https://www.rabbitmq.com/"><img alt="RabbitMQ" src="https://img.shields.io/badge/RabbitMQ-FF6600?logo=rabbitmq&logoColor=white&style=for-the-badge"></a> <img alt="AI" src="https://img.shields.io/badge/gpt4free-6A5ACD?style=for-the-badge&logo=openai&logoColor=white"> <img alt="cAdvisor" src="https://img.shields.io/badge/cAdvisor-0A66C2?style=for-the-badge&logo=cadvisor&logoColor=white"> <img alt="Node Exporter" src="https://img.shields.io/badge/node_exporter-4C9A2A?style=for-the-badge&logoColor=white">
</div>

- **Инфраструктура:** `Docker`, `docker-compose`
- **Мониторинг:** `Prometheus`, `Grafana`
- **AI/LLM:** локальный сервис `gpt4free` для анализа и генерации дашбордов/рекомендаций

## 🧑‍💻 О проекте / About the project

Интеллектуальная open-source система сбора, анализа и визуализации метрик/логов с AI‑ассистентом. Поддерживает автоматизацию мониторинга, генерацию запросов, построение дашбордов, и выработку рекомендаций по реагированию на инциденты с использованием LLM.

## ✨ Демонстрация / Demo

- Ниже представлена демонстрация работы анализа логов и создания дашбордов:

  <table>
    <tr>
      <td><img src="docs/demo0.gif" alt="Auto collect" width="600" /></td>
      <td>
        <b> 🕹️ Быстрый старт / Quick start</b><br>
        Весь проект уже обернут в docker-cokpose. Его можно использовать для новых проектов.
      </td>
    </tr>
  </table>
  
  <table align="right">
    <tr>
      </td>
      <td><img src="docs/demo1.gif" alt="Auto collect" width="600" /></td>
      <td>
        <b> 🔩 Анализ логов / Logs analyzer </b><br>
        Передаём логи и алерты ИИ для анализа и описания проблемы.
    </tr>
  </table>
  
  <table>
    <tr>
      <td><img src="docs/demo2.gif" alt="Auto collect" width="600" /></td>
      <td>
        <b> 📊 ИИ Дашборды / LLM Dashboards</b><br>
        Генерируем дашборды для Grafana используя естественный язык.
      </td>
    </tr>
  </table>

</div>

- Полное видео:

<div align="center">
<a href="https://drive.google.com/file/d/1RQCVaLSbbzl4DI2u4CnZSYgbNG6iQf_J/view?usp=sharing" target="_blank">
<img src="https://raw.githubusercontent.com/VsevolodLazebnyi/telecom-ai-monitoring-hackathon/main/docs/view0.png" alt="Watch the video" width="600">
</a>
</div>

## 🏛️ Архитектура и компоненты / Architecture & Components

- **Prometheus** — сбор и хранение метрик (порт `9090`). Конфиг: `./config/prometheus.yml`.
- **Grafana** — визуализация и дашборды (порт `3000`). Провижининг: `./grafana/provisioning`, загружаемые дашборды: `./generated_dashboards`.
- **cAdvisor** — метрики контейнеров (порт `8080`).
- **node-exporter** — системные метрики хоста (порт `9100`).
- **redis-exporter** — метрики Redis (порт `9121`).
- **Redis** — кэш/источник метрик симуляторов (порт `6379`, локальный пароль в compose: `admin123`).
- **PostgreSQL** — база данных приложения (порт `5432`, БД `telecom_db`).
- **postgres-exporter** — метрики PostgreSQL (порт `9187`).
- **RabbitMQ** — брокер сообщений для симуляторов (порты `5672`, `15672`).
- **gpt4free** — локальный AI‑сервис для генерации/анализа (доступен на `127.0.0.1:1337`).
- **telecom-simulator** — генерация событий/нагрузки; использует RabbitMQ и Redis.
- **telecom-monitoring-console** — UI интерфейс (порт `8501`), подключается к Prometheus/Grafana и локальному gpt4free.

## 🚀 Быстрый старт / Quick Start

### Требования / Requirements
- Установленные Docker и docker‑compose
- Ресурсы: минимум 4 GB RAM и 4 CPU

### Установка и запуск / Setup & Run
1) Клонируйте репозиторий:
```bash
git clone telecom-ai-monitoring-hackathon
```

2) Перейдите в директорию проекта:
```bash
cd /path/to/telecom-ai-monitoring-hackathon
```

3) Запустите сборку контейнера:
```bash
docker-compose up -d --build
```

- Эта команда соберёт образы (там, где указан `build`) и поднимет все сервисы.

- Интерфейс: http://localhost:8501
  
- Grafana: http://localhost:3000 (логин/пароль по умолчанию: `admin/admin`)
- Prometheus: http://localhost:9090

## 📊 Дашборды и эндпоинты / Dashboards & Endpoints

- Grafana: http://localhost:3000 (admin/admin)
- Prometheus: http://localhost:9090
- cAdvisor: http://localhost:8080
- Postgres Exporter: http://localhost:9187
- Node Exporter: http://localhost:9100
- Redis Exporter: http://localhost:9121
- RabbitMQ Management: http://localhost:15672 (admin / `admin123`)

## 🤖 Использование AI и LLM / AI & LLM Usage

- Включён локальный сервис **gpt4free** (контейнер `g4f`), к которому обращается `...`.
- Применения:
  - автоматический поиск метрик,
  - помощь в отладке и расследовании инцидентов,
  - генерация PromQL‑запросов и Grafana‑дашбордов,
  - рекомендации по устранению проблем на основе логов.

## 🧪 Применение в МТС/Телеком / Telecom Use‑Cases

- Автоматизация мониторинга сервисов.
- Ускорение работы с Дашбордами и анализом метрик.

Ожидаемые эффекты:
- ускорение деплоя,
- сокращение времени расследования инцидентов,
- экономия за счёт автоматизации рутинных операций.

## 📂 Структура проекта / Project Structure

```
Project
├── Dockerfile
├── alerts
│   └── telecom_alerts.yaml
├── chroma_db
│   └── chroma.sqlite3
├── config
│   └── prometheus.yml
├── docker-compose.yaml
├── grafana
│   └── provisioning
│       ├── dashboards
│       │   └── dashboard.yml
│       └── datasources
│           └── prometheus.yml
├── handlers
│   ├── gpt4free_handler.py
│   ├── grafana_handler.py
│   ├── postgres_handler.py
│   ├── prometheus_handler.py
│   ├── rabbitmq_handler.py
│   └── vectordb_handler.py
├── main.py
├── requirements.txt
└── simulators
    ├── Dockerfile
    ├── requirements.txt
    └── telecom_data_simulator.py
```

## 📑 Лицензия / License
> [!IMPORTANT]\
> Этот проект распространяется как opensource проект. Подробнее см. в файле [LICENSE](LICENSE).

---

<div align="center">

⭐ **Если проект вам понравился, не забудьте поставить звезду!** / **Don't forget star!**

</div>
