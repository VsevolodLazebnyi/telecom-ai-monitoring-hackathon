import requests
import json
import uuid
from loguru import logger

class Gpt4FreeHandler:
    def __init__(self, base_url: str = "http://gpt4free:1337"):
        self.base_url = base_url

    def gpt4free_request(self, prompt: str) -> str:
        try:
            url = f"{self.base_url}/v1/chat/completions"
            payload = {
                "model": "gpt-4",
                "messages": [{"role": "user", "content": prompt}]
            }
            response = requests.post(url, json=payload, timeout=120)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except requests.exceptions.RequestException as e:
            logger.error(f"GPT4Free API request failed: {str(e)}")
            return json.dumps({"error": f"GPT4Free request failed: {str(e)}"})
        except Exception as e:
            logger.error(f"Unexpected error in GPT4Free handler: {str(e)}")
            return json.dumps({"error": f"Unexpected error: {str(e)}"})

    def _strip_code_fences(self, text: str) -> str:
        if not isinstance(text, str):
            return text
        t = text.strip()
        if t.startswith("```"):
            t = t.strip("`").strip()
        if t.lower().startswith("json"):
            t = t[4:].strip()
        return t

    def generate_promql_query(self, user_query_map: dict) -> dict:
        prompt = f"""
Return ONLY valid JSON. No markdown. No comments. No extra text.
Context: You generate PromQL queries for Prometheus.
Input:
{json.dumps(user_query_map, indent=4, ensure_ascii=False)}
Output schema:
{{
  "result": [
    {{
      "mandatory_datasource_uuid": "string",
      "userquery": "string",
      "query": "promql string"
    }}
  ]
}}
"""
        result = self.gpt4free_request(prompt)
        try:
            result = self._strip_code_fences(result)
            return json.loads(result)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse GPT4Free response: {e}; raw: {result[:500]}")
            return {"error": "Failed to parse JSON response from GPT4Free"}

    def generate_grafana_dashboard(self, query_responses: list) -> dict:
        prompt = f"""
Return ONLY valid JSON. No markdown. No comments. No extra text.
Task: Build a valid Grafana 9.x dashboard JSON from the provided panel specs.
Rules:
- Output must be a single JSON object compatible with Grafana /api/dashboards/db.
- Include fields: "title", "uid", "time", "timezone", "schemaVersion", "panels" (array).
- For each panel:
  - Must include "type", "title", "gridPos".
  - "datasource" must be an object: {{"type":"prometheus"|"postgres","uid":"..."}}
  - For Prometheus: use "targets": [{{"expr":"...","refId":"A","format":"time_series"|"table"}}]
  - For Postgres: use "targets": [{{"rawSql":"...","refId":"A","format":"table"|"time_series"}}]
  - Add sensible defaults: "options": {{}}, "fieldConfig": {{"defaults": {{}}, "overrides": []}}
- No links, no markdown.
Input panels:
{json.dumps(query_responses, indent=2, ensure_ascii=False)}
"""
        raw = self.gpt4free_request(prompt)
        try:
            raw = self._strip_code_fences(raw)
            data = json.loads(raw)
        except json.JSONDecodeError as e:
            logger.error(f"Dashboard JSON parse failed: {e}; raw: {raw[:500]}")
            return {"error": "Failed to parse JSON from GPT4Free"}

        try:
            if not isinstance(data, dict):
                return {"error": "Dashboard is not an object"}
            data.setdefault("title", "Generated Dashboard")
            data.setdefault("timezone", "browser")
            data.setdefault("schemaVersion", 36)
            data.setdefault("time", {"from": "now-6h", "to": "now"})
            if "uid" not in data or not data["uid"]:
                data["uid"] = f"auto-{uuid.uuid4().hex[:12]}"

            panels = data.get("panels", [])
            if not isinstance(panels, list) or len(panels) == 0:
                return {"error": "Dashboard has no panels"}
            for i, p in enumerate(panels):
                p.setdefault("title", f"Panel {i+1}")
                p.setdefault("gridPos", {"x": 0, "y": i*8, "w": 12, "h": 8})
                
                ds = p.get("datasource")
                if isinstance(ds, str):
                    typ = "prometheus" if "prom" in ds.lower() else "postgres"
                    p["datasource"] = {"type": typ, "uid": ds}
                elif isinstance(ds, dict):
                    p["datasource"].setdefault("type", "prometheus")
                    p["datasource"].setdefault("uid", "default")
                else:
                    p["datasource"] = {"type": "prometheus", "uid": "default"}
                    
                if "targets" not in p or not p["targets"]:
                    return {"error": f"Panel {i+1} has no targets"}
                for t in p["targets"]:
                    t.setdefault("refId", "A")
                    if p["datasource"]["type"] == "prometheus":
                        if "expr" not in t:
                            return {"error": f"Panel {i+1} target missing expr"}
                        t.setdefault("format", "time_series")
                    elif p["datasource"]["type"] == "postgres":
                        if "rawSql" not in t:
                            return {"error": f"Panel {i+1} target missing rawSql"}
                        t.setdefault("format", "table")
                p.setdefault("fieldConfig", {"defaults": {}, "overrides": []})
                p.setdefault("options", {})
            return data
        except Exception as e:
            logger.error(f"Dashboard post-processing failed: {e}")
            return {"error": f"Dashboard post-processing failed: {str(e)}"}

    def analyze_alert_with_ai(self, alert_data: dict) -> str:
        prompt = f"""
        You are an experienced telecom engineer at MTS. Analyze the following alert and provide a detailed explanation in Russian.

        Alert data:
        {json.dumps(alert_data, indent=2, ensure_ascii=False)}

        Response structure:
        1. **Problem type**: Briefly describe what happened.
        2. **Possible causes**: 2-3 most likely technical or business causes.
        3. **Customer impact**: How will the subscriber feel this?
        4. **Recommended actions**: What should an engineer check?

        Answer clearly and to the point. Only in Russian.
        """
        
        return self.gpt4free_request(prompt)