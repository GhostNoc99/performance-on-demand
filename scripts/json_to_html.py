import json
from pathlib import Path

json_path = Path("report_gitactions/summary.json")
html_path = Path("report_gitactions/summary.html")

if not json_path.exists():
    raise FileNotFoundError(f"No existe el archivo {json_path}")

with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)

metrics = data.get("metrics", {})

def get_metric_value(metric_name, field, default="N/A"):
    metric = metrics.get(metric_name, {})
    values = metric.get("values", {})
    return values.get(field, default)

checks_total = get_metric_value("checks", "passes", 0)
checks_fails = get_metric_value("checks", "fails", 0)
http_reqs = get_metric_value("http_reqs", "count", 0)
http_failed = get_metric_value("http_req_failed", "rate", "N/A")
avg_duration = get_metric_value("http_req_duration", "avg", "N/A")
p90_duration = get_metric_value("http_req_duration", "p(90)", "N/A")
p95_duration = get_metric_value("http_req_duration", "p(95)", "N/A")
iterations = get_metric_value("iterations", "count", 0)

html = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Reporte k6</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 40px;
            background: #f7f7f7;
            color: #222;
        }}
        h1 {{
            color: #111;
        }}
        .card {{
            background: white;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th, td {{
            padding: 12px;
            border-bottom: 1px solid #ddd;
            text-align: left;
        }}
        th {{
            background: #f0f0f0;
        }}
    </style>
</head>
<body>
    <h1>Reporte de Performance k6</h1>

    <div class="card">
        <h2>Resumen</h2>
        <table>
            <tr><th>Métrica</th><th>Valor</th></tr>
            <tr><td>Checks exitosos</td><td>{checks_total}</td></tr>
            <tr><td>Checks fallidos</td><td>{checks_fails}</td></tr>
            <tr><td>Total requests</td><td>{http_reqs}</td></tr>
            <tr><td>Tasa de error HTTP</td><td>{http_failed}</td></tr>
            <tr><td>Duración promedio</td><td>{avg_duration}</td></tr>
            <tr><td>P90</td><td>{p90_duration}</td></tr>
            <tr><td>P95</td><td>{p95_duration}</td></tr>
            <tr><td>Iteraciones</td><td>{iterations}</td></tr>
        </table>
    </div>

    <div class="card">
        <h2>JSON completo</h2>
        <pre>{json.dumps(data, indent=2, ensure_ascii=False)}</pre>
    </div>
</body>
</html>
"""

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html)

print(f"HTML generado en: {html_path}")