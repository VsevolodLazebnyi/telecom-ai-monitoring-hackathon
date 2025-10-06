import os
import json
import time
import threading
from datetime import datetime, timedelta

import requests
import pandas as pd
import streamlit as st
import redis
from loguru import logger

from handlers.gpt4free_handler import Gpt4FreeHandler
from handlers.grafana_handler import GrafanaHandler
from handlers.prometheus_handler import PrometheusHandler
from handlers.rabbitmq_handler import RabbitMQHandler
from handlers.vectordb_handler import VectorDBHandler

APP_TITLE = "Умный мониторинг с ИИ"
st.set_page_config(page_title=APP_TITLE, page_icon="📡", layout="wide")

def get_default_envs():
    return {
        "PROMETHEUS_URL": os.getenv("PROMETHEUS_URL", "http://localhost:9090"),
        "GRAFANA_URL": os.getenv("GRAFANA_URL", "http://localhost:3000"),
        "GRAFANA_API_KEY": os.getenv("glsa_CR1KUKUEXjXsZsO72sGV0JGbJEm2Aj5y_4e2e5639", "glsa_CR1KUKUEXjXsZsO72sGV0JGbJEm2Aj5y_4e2e5639"),
        "REDIS_URL": os.getenv("REDIS_URL", "redis://:admin123@localhost:6379/0"),
        "RABBITMQ_URL": os.getenv("RABBITMQ_URL", "amqp://admin:admin123@localhost:5672/"),
        "GPT4FREE_URL": os.getenv("GPT4FREE_URL", "http://localhost:1337"),
    }

def init_session_state():
    if "cfg" not in st.session_state:
        st.session_state.cfg = get_default_envs()

    if "gpt" not in st.session_state:
        st.session_state.gpt = Gpt4FreeHandler(base_url=st.session_state.cfg["GPT4FREE_URL"])
    if "grafana" not in st.session_state:
        st.session_state.grafana = GrafanaHandler(
            grafana_host=st.session_state.cfg["GRAFANA_URL"],
            grafana_token=st.session_state.cfg["GRAFANA_API_KEY"],
        )
    if "prom" not in st.session_state:
        st.session_state.prom = PrometheusHandler(url=st.session_state.cfg["PROMETHEUS_URL"])
    if "vectordb" not in st.session_state:
        st.session_state.vectordb = VectorDBHandler()

    try:
        st.session_state.redis = redis.Redis.from_url(
            st.session_state.cfg["REDIS_URL"], decode_responses=True
        )
    except Exception as e:
        st.session_state.redis = None
        logger.error(f"Ошибка инициализации Redis: {e}")

    if "rabbit_consumer_started" not in st.session_state:
        st.session_state.rabbit_consumer_started = False

def sidebar_config():
    st.sidebar.header("Подключения")
    cfg = st.session_state.cfg

    cfg["PROMETHEUS_URL"] = st.sidebar.text_input("Prometheus URL", cfg["PROMETHEUS_URL"])
    cfg["GRAFANA_URL"] = st.sidebar.text_input("Grafana URL", cfg["GRAFANA_URL"])
    cfg["REDIS_URL"] = st.sidebar.text_input("Redis URL", cfg["REDIS_URL"])
    cfg["RABBITMQ_URL"] = st.sidebar.text_input("RabbitMQ URL", cfg["RABBITMQ_URL"])
    cfg["GPT4FREE_URL"] = st.sidebar.text_input("GPT4Free URL", cfg["GPT4FREE_URL"])

    col_a, col_b = st.sidebar.columns(2)
    if col_a.button("Сохранить", use_container_width=True):
        st.session_state.gpt = Gpt4FreeHandler(base_url=cfg["GPT4FREE_URL"])
        st.session_state.grafana = GrafanaHandler(grafana_host=cfg["GRAFANA_URL"], grafana_token=cfg["GRAFANA_API_KEY"])
        st.session_state.prom = PrometheusHandler(url=cfg["PROMETHEUS_URL"])
        try:
            st.session_state.redis = redis.Redis.from_url(cfg["REDIS_URL"], decode_responses=True)
            st.success("Переподключение с обновленной конфигурацией успешно.")
        except Exception as e:
            st.error(f"Ошибка переподключения Redis: {e}")

    if col_b.button("RabbitMQ", use_container_width=True, disabled=st.session_state.rabbit_consumer_started):
        try:
            def start_consumer():
                try:
                    RabbitMQHandler()
                except Exception as e_:
                    logger.error(f"Ошибка потока Rabbit consumer: {e_}")

            t = threading.Thread(target=start_consumer, daemon=True)
            t.start()
            st.session_state.rabbit_consumer_started = True
            st.success("RabbitMQ consumer запущен.")
        except Exception as e:
            st.error(f"Не удалось запустить consumer: {e}")

def check_prometheus(url: str) -> tuple[bool, str]:
    try:
        r = requests.get(f"{url}/api/v1/status/buildinfo", timeout=5)
        return (r.ok, f"{r.status_code}")
    except Exception as e:
        return (False, str(e))

def check_grafana(url: str, key: str) -> tuple[bool, str]:
    try:
        headers = {"Authorization": f"Bearer {key}"} if key else {}
        r = requests.get(f"{url}/api/health", headers=headers, timeout=5)
        return (r.ok, f"{r.status_code}")
    except Exception as e:
        return (False, str(e))

def check_redis(redis_client) -> tuple[bool, str]:
    try:
        if not redis_client:
            return (False, "не инициализирован")
        pong = redis_client.ping()
        return (pong is True, "PONG" if pong else "нет ответа")
    except Exception as e:
        return (False, str(e))

def check_rabbitmq(amqp_url: str) -> tuple[bool, str]:
    try:
        mgmt = "http://localhost:15672/api/overview"
        r = requests.get(mgmt, auth=("admin", "admin123"), timeout=5)
        return (r.ok, f"{r.status_code}")
    except Exception as e:
        return (False, str(e))

def check_gpt4free(url: str) -> tuple[bool, str]:
    try:
        payload = {
            "model": "gpt-4",
            "messages": [{"role": "user", "content": "ping"}],
            "max_tokens": 5,
            "temperature": 0.0,
        }
        r = requests.post(f"{url}/v1/chat/completions", json=payload, timeout=10)
        return (r.ok, f"{r.status_code}")
    except Exception as e:
        return (False, str(e))

def prom_instant_query(base_url: str, query: str):
    try:
        r = requests.get(f"{base_url}/api/v1/query", params={"query": query}, timeout=20)
        return r.ok, (r.json() if r.ok else r.text)
    except Exception as e:
        return False, str(e)

def prom_range_query(base_url: str, query: str, start: datetime, end: datetime, step: str = "15s"):
    try:
        params = {
            "query": query,
            "start": int(start.timestamp()),
            "end": int(end.timestamp()),
            "step": step,
        }
        r = requests.get(f"{base_url}/api/v1/query_range", params=params, timeout=30)
        return r.ok, (r.json() if r.ok else r.text)
    except Exception as e:
        return False, str(e)

def matrix_to_dataframe(result: list):
    rows = []
    for series in result:
        metric = series.get("metric", {})
        label = metric.get("instance") or metric.get("pod") or metric.get("__name__") or json.dumps(metric, ensure_ascii=False)
        for ts, val in series.get("values", []):
            ts_dt = datetime.fromtimestamp(float(ts))
            rows.append({"timestamp": ts_dt, "series": label, "value": float(val)})
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    pivot = df.pivot(index="timestamp", columns="series", values="value").sort_index()
    return pivot

def vector_to_dataframe(result: list):
    rows = []
    for series in result:
        metric = series.get("metric", {})
        value = series.get("value")
        val = float(value[1]) if value and len(value) > 1 else None
        rows.append({"metric": json.dumps(metric, ensure_ascii=False), "value": val})
    return pd.DataFrame(rows)

def tab_status():
    st.markdown("### Статус системы")
    cfg = st.session_state.cfg

    col1, col2, col3 = st.columns(3)
    with col1:
        ok, info = check_prometheus(cfg["PROMETHEUS_URL"])
        st.metric("Prometheus", "UP" if ok else "DOWN", delta=info)
    with col2:
        ok, info = check_grafana(cfg["GRAFANA_URL"], cfg["GRAFANA_API_KEY"])
        st.metric("Grafana", "UP" if ok else "DOWN", delta=info)
    with col3:
        ok, info = check_redis(st.session_state.redis)
        st.metric("Redis", "UP" if ok else "DOWN", delta=info)

    col4, col5 = st.columns(2)
    with col4:
        ok, info = check_rabbitmq(cfg["RABBITMQ_URL"])
        st.metric("RabbitMQ", "UP" if ok else "DOWN", delta=info)
    with col5:
        ok, info = check_gpt4free(cfg["GPT4FREE_URL"])
        st.metric("GPT4Free", "UP" if ok else "DOWN", delta=info)

def resolve_grafana_prometheus_uid_and_url():
    ds_uid = None
    prom_base_url = st.session_state.cfg["PROMETHEUS_URL"]

    if not st.session_state.cfg["GRAFANA_API_KEY"]:
        return ds_uid, prom_base_url

    try:
        datasources = st.session_state.grafana.fetch_datasources()
        prom_list = [d for d in datasources if d.get("typeName") == "Prometheus" or d.get("name") == "prometheus"]
        if prom_list:
            ds = prom_list[0]
            ds_uid = ds.get("uid")
        return ds_uid, prom_base_url
    except Exception as e:
        st.warning(f"Не удалось получить datasources из Grafana: {e}")
        return ds_uid, prom_base_url
    
def save_dashboard_to_provisioning(dashboard_json, filename):
    dashboard_dir = "./generated_dashboards"
    os.makedirs(dashboard_dir, exist_ok=True)
    safe_filename = "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_')).rstrip()
    safe_filename = safe_filename.replace(' ', '_') + ".json"
    
    filepath = os.path.join(dashboard_dir, safe_filename)
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(dashboard_json, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Дашборд сохранен в {filepath}")
        return filepath
    except Exception as e:
        logger.error(f"Ошибка сохранения дашборда: {e}")
        return None

def tab_metrics_vectordb():
    st.markdown("### Каталог метрик и VectorDB")

    ds_uid, prom_url = resolve_grafana_prometheus_uid_and_url()
    if ds_uid:
        st.success(f"Grafana Prometheus DS UID: {ds_uid}")
    else:
        st.info("Grafana API ключ не установлен или Prometheus datasource не найден.")

    ds_uid_input = st.text_input("Datasource UID", ds_uid or "default")

    if st.button("🔄 Синхронизировать метрики → VectorDB"):
        try:
            count = st.session_state.prom.fetch_metrics_data(
                ds={"uid": ds_uid_input},
                vectordbs_handler=st.session_state.vectordb,
            )
            st.success(f"Синхронизировано новых метрик: {count}")
        except Exception as e:
            st.error(f"Ошибка синхронизации: {e}")

    st.divider()
    st.markdown("#### Поиск похожих метрик")
    examples = st.text_input("Введите названия метрик через запятую")
    topn = st.slider("Количество результатов", 1, 10, 3)
    if st.button("🔍 Найти похожие"):
        names = [x.strip() for x in examples.split(",") if x.strip()]
        if not names:
            st.warning("Введите метрики для поиска.")
        else:
            sims = st.session_state.vectordb.query_metrics_batch(names, ds_uid=ds_uid_input, n_results=topn)
            if sims:
                st.success(f"Похожие метрики ({len(sims)}):")
                st.write(sims)
            else:
                st.info("Ничего не найдено.")

def tab_ai_dashboard():
    st.markdown("### Генерация дашбордов с ИИ")
    
    if not st.session_state.grafana.test_connection():
        st.error("❌ Не удалось подключиться к Grafana. Проверьте URL и токен в настройках.")
        return
    
    ds_uid, prom_url = resolve_grafana_prometheus_uid_and_url()
    ds_uid = ds_uid or "default"
    
    st.info("💡 Опишите метрики для дашборда")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        dashboard_queries = st.text_area(
            "Запросы для панелей:",
            height=150,
            placeholder="Загрузка CPU по контейнерам\nИспользование памяти Redis\nКоличество HTTP запросов\nОшибки подключения к БД"
        )
        
    with col2:
        dashboard_title = st.text_input("Название дашборда", "AI-dashboard")
        time_range = st.selectbox("Временной диапазон", ["1h", "6h", "24h", "7d"], index=1)
        
        folders = st.session_state.grafana.get_folders()
        folder_options = {0: "AI Generated Dashboards"}
        for folder in folders:
            folder_options[folder['id']] = folder['title']
        
        selected_folder = st.selectbox("Папка", options=list(folder_options.keys()), 
                                     format_func=lambda x: folder_options[x])

    if st.button("Сгенерировать дашборд", type="primary"):
        if not dashboard_queries.strip():
            st.warning("Введите запросы для панелей")
            return
            
        queries = [q.strip() for q in dashboard_queries.split("\n") if q.strip()]
        if not queries:
            st.warning("Нет валидных запросов")
            return
            
        st.info(f"Генерация дашборда с {len(queries)} панелями...")
        
        panels = []
        errors = []
        
        with st.status("Создание панелей...", expanded=True) as status:
            for i, query in enumerate(queries):
                status.write(f"Панель {i+1}: {query}")
                
                user_query_map = {
                    "mandatory_datasource_uuid": ds_uid,
                    "userquery": query,
                    "time_range": time_range,
                    "hints": ["use available metric names", "prefer standard exporters"]
                }
                
                promql_result = st.session_state.gpt.generate_promql_query(user_query_map)
                
                if "error" in promql_result:
                    errors.append(f"❌ '{query}': {promql_result['error']}")
                    continue
                    
                try:
                    result_arr = promql_result.get("result", [])
                    if not result_arr:
                        errors.append(f"❌ '{query}': пустой ответ от ИИ")
                        continue
                        
                    promql = result_arr[0].get("query", "")
                    if not promql:
                        errors.append(f"❌ '{query}': не сгенерирован PromQL")
                        continue
                        
                    if any(op in promql.lower() for op in ["rate(", "increase(", "histogram_quantile"]):
                        panel_type = "timeseries"
                        format_type = "time_series"
                    else:
                        panel_type = "stat"
                        format_type = "table"
                    
                    panel = {
                        "title": query[:80],
                        "datasource": {"type": "prometheus", "uid": ds_uid},
                        "query": promql,
                        "format": format_type,
                        "vis_type": panel_type,
                        "gridPos": {"x": (i % 2) * 12, "y": (i // 2) * 8, "w": 12, "h": 8}
                    }
                    panels.append(panel)
                    status.write(f"✅ Создана панель с PromQL: `{promql[:50]}...`")
                    
                except Exception as e:
                    errors.append(f"❌ '{query}': ошибка обработки - {str(e)}")
            
            if errors:
                status.update(label="Завершено с ошибками", state="error")
                st.error("Ошибки генерации:")
                for error in errors:
                    st.write(error)
            else:
                status.update(label="Все панели успешно созданы!", state="complete")
        
        if panels:
            with st.status("Построение дашборда...", expanded=True) as status:
                status.write("Генерация JSON структуры дашборда...")
                
                dashboard_data = {
                    "dashboard_title": dashboard_title,
                    "time_range": time_range,
                    "panels": panels
                }
                
                dash_json = st.session_state.gpt.generate_grafana_dashboard(dashboard_data)
                
                if "error" in dash_json:
                    status.update(label="Ошибка генерации дашборда", state="error")
                    st.error(f"Ошибка: {dash_json['error']}")
                    return
                
                status.update(label="Дашборд успешно сгенерирован!", state="complete")
            
            with st.expander("📋 Просмотр сгенерированного JSON"):
                st.json(dash_json)
            
            st.markdown("---")
            st.subheader("Импорт в Grafana")
            
            col_import1, col_import2 = st.columns([1, 1])
            
            with col_import1:
                if st.button("📁 Сохранить в Grafana", use_container_width=True, 
                           help="Сохранить дашборд в файл для провижининга Grafana"):
                    filepath = save_dashboard_to_provisioning(dash_json, dashboard_title)
                    if filepath:
                        st.success(f"✅ Сохранено в: `{filepath}`")
                    else:
                        st.error("❌ Ошибка сохранения файла дашборда")
            
            with col_import2:
                st.download_button(
                    label="💾 Скачать JSON",
                    data=json.dumps(dash_json, indent=2, ensure_ascii=False),
                    file_name=f"{dashboard_title.lower().replace(' ', '_')}.json",
                    mime="application/json",
                    use_container_width=True
                )

def tab_alerts_logs():
    st.markdown("### ИИ анализ")
    col_r1, col_r2 = st.columns([1, 1])
    with col_r1:
        limit = st.slider("Сколько последних оповещений показать", 10, 200, 50, 10)
    with col_r2:
        analyze_ai = st.checkbox("Анализировать оповещения с ИИ", value=False)
    
    if st.button("Обновить сейчас"):
        if hasattr(st, "rerun"):
            st.rerun()
        else:
            st.experimental_rerun()
            
    try:
        r = st.session_state.redis
        if not r:
            st.error("Redis не инициализирован.")
            return
            
        cursor = 0
        keys = []
        while True:
            cursor, batch = r.scan(cursor=cursor, match="alert:*", count=500)
            keys.extend(batch)
            if cursor == 0:
                break
        keys_sorted = sorted(keys, reverse=True)[:limit]
        if not keys_sorted:
            st.info("Оповещений пока нет.")
            return
            
        items = []
        for k in keys_sorted:
            try:
                val = r.get(k)
                if val:
                    items.append(json.loads(val))
            except Exception:
                continue
                
        for alert in items:
            severity = alert.get("severity", "INFO")
            color = {
                "CRITICAL": "🟥",
                "HIGH": "🟧",
                "WARNING": "🟨",
                "MEDIUM": "🟨",
                "INFO": "🟦",
            }.get(severity, "⬜")
            st.write(f"{color} [{alert.get('timestamp','')}] {alert.get('type','')}")
            st.json(alert, expanded=False)
            if analyze_ai:
                with st.spinner("Анализ ИИ..."):
                    explanation = st.session_state.gpt.analyze_alert_with_ai(alert)
                st.markdown("**Анализ ИИ:**")
                st.write(explanation)
    except Exception as e:
        st.error(f"Ошибка чтения из Redis: {e}")

def main():
    init_session_state()
    sidebar_config()
    st.title(APP_TITLE)
    tabs = st.tabs([
        "ИИ → Дашборды",
        "Оповещения и логи", 
        "Статус",
        "Каталог метрик"
    ])
    with tabs[0]: tab_ai_dashboard()
    with tabs[1]: tab_alerts_logs()
    with tabs[2]: tab_status()
    with tabs[3]: tab_metrics_vectordb()
    

if __name__ == "__main__":
    main()