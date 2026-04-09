import json
from pathlib import Path
from datetime import datetime

report_dir = Path("report_gitactions")

json_files = sorted(report_dir.glob("summary-*.json"))
if not json_files:
    raise FileNotFoundError("No se encontró ningún summary JSON en report_gitactions")

latest_json = json_files[-1]
html_file = latest_json.with_suffix(".html")

with open(latest_json, "r", encoding="utf-8") as f:
    data = json.load(f)

metrics = data.get("metrics", {})

def get_metric(metric_name, field, default="N/A"):
    return metrics.get(metric_name, {}).get("values", {}).get(field, default)

checks_pass = get_metric("checks", "passes", 0)
checks_fail = get_metric("checks", "fails", 0)
http_reqs = get_metric("http_reqs", "count", 0)
http_failed = get_metric("http_req_failed", "rate", 0)
avg_duration = get_metric("http_req_duration", "avg", "N/A")
p90_duration = get_metric("http_req_duration", "p(90)", "N/A")
p95_duration = get_metric("http_req_duration", "p(95)", "N/A")
iterations = get_metric("iterations", "count", 0)

try:
    http_failed_num = float(http_failed)
except Exception:
    http_failed_num = 1

status = "PASS" if checks_fail == 0 and http_failed_num == 0 else "FAIL"
status_class = "pass" if status == "PASS" else "fail"

generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

html = f"""
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Reporte k6</title>
  <style>
    * {{
      box-sizing: border-box;
    }}

    body {{
      margin: 0;
      font-family: Arial, Helvetica, sans-serif;
      background: #f4f7fb;
      color: #1f2937;
    }}

    .container {{
      max-width: 1200px;
      margin: 0 auto;
      padding: 32px 20px;
    }}

    .header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 20px;
      flex-wrap: wrap;
      margin-bottom: 24px;
    }}

    .title-block h1 {{
      margin: 0;
      font-size: 32px;
      color: #111827;
    }}

    .title-block p {{
      margin: 8px 0 0;
      color: #6b7280;
      font-size: 14px;
    }}

    .badge {{
      padding: 12px 20px;
      border-radius: 999px;
      font-weight: bold;
      font-size: 14px;
      color: white;
      min-width: 110px;
      text-align: center;
      box-shadow: 0 6px 18px rgba(0,0,0,0.12);
    }}

    .badge.pass {{
      background: linear-gradient(135deg, #16a34a, #22c55e);
    }}

    .badge.fail {{
      background: linear-gradient(135deg, #dc2626, #ef4444);
    }}

    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 18px;
      margin-bottom: 28px;
    }}

    .card {{
      background: white;
      border-radius: 18px;
      padding: 22px;
      box-shadow: 0 10px 25px rgba(15, 23, 42, 0.08);
      border: 1px solid #e5e7eb;
    }}

    .card h3 {{
      margin: 0 0 10px;
      font-size: 14px;
      color: #6b7280;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }}

    .metric {{
      font-size: 30px;
      font-weight: bold;
      color: #111827;
    }}

    .subtext {{
      margin-top: 8px;
      font-size: 13px;
      color: #6b7280;
    }}

    .section {{
      background: white;
      border-radius: 18px;
      padding: 24px;
      box-shadow: 0 10px 25px rgba(15, 23, 42, 0.08);
      border: 1px solid #e5e7eb;
      margin-bottom: 24px;
    }}

    .section h2 {{
      margin-top: 0;
      margin-bottom: 18px;
      font-size: 22px;
      color: #111827;
    }}

    table {{
      width: 100%;
      border-collapse: collapse;
      overflow: hidden;
      border-radius: 12px;
    }}

    th, td {{
      padding: 14px 16px;
      border-bottom: 1px solid #e5e7eb;
      text-align: left;
      font-size: 14px;
    }}

    th {{
      background: #f9fafb;
      color: #374151;
    }}

    tr:last-child td {{
      border-bottom: none;
    }}

    .pill {{
      display: inline-block;
      padding: 6px 12px;
      border-radius: 999px;
      font-size: 12px;
      font-weight: bold;
      color: white;
    }}

    .pill.pass {{
      background: #16a34a;
    }}

    .pill.fail {{
      background: #dc2626;
    }}

    details {{
      margin-top: 10px;
    }}

    summary {{
      cursor: pointer;
      font-weight: bold;
      color: #2563eb;
      margin-bottom: 12px;
    }}

    pre {{
      background: #0f172a;
      color: #e5e7eb;
      padding: 18px;
      border-radius: 14px;
      overflow-x: auto;
      font-size: 12px;
      line-height: 1.5;
    }}

    .footer {{
      text-align: center;
      font-size: 12px;
      color: #6b7280;
      margin-top: 20px;
    }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <div class="title-block">
        <h1>Reporte de Performance k6</h1>
        <p><strong>Archivo:</strong> {latest_json.name}</p>
        <p><strong>Generado:</strong> {generated_at}</p>
      </div>
      <div class="badge {status_class}">{status}</div>
    </div>

    <div class="grid">
      <div class="card">
        <h3>Total Requests</h3>
        <div class="metric">{http_reqs}</div>
        <div class="subtext">Solicitudes HTTP ejecutadas</div>
      </div>

      <div class="card">
        <h3>Checks Exitosos</h3>
        <div class="metric">{checks_pass}</div>
        <div class="subtext">Validaciones aprobadas</div>
      </div>

      <div class="card">
        <h3>Checks Fallidos</h3>
        <div class="metric">{checks_fail}</div>
        <div class="subtext">Validaciones fallidas</div>
      </div>

      <div class="card">
        <h3>Error Rate</h3>
        <div class="metric">{http_failed}</div>
        <div class="subtext">Tasa de error HTTP</div>
      </div>

      <div class="card">
        <h3>Avg Duration</h3>
        <div class="metric">{avg_duration}</div>
        <div class="subtext">Tiempo promedio de respuesta</div>
      </div>

      <div class="card">
        <h3>P95</h3>
        <div class="metric">{p95_duration}</div>
        <div class="subtext">Percentil 95</div>
      </div>
    </div>

    <div class="section">
      <h2>Resumen Ejecutivo</h2>
      <table>
        <thead>
          <tr>
            <th>Métrica</th>
            <th>Valor</th>
            <th>Estado</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>Iteraciones</td>
            <td>{iterations}</td>
            <td><span class="pill pass">INFO</span></td>
          </tr>
          <tr>
            <td>HTTP Requests</td>
            <td>{http_reqs}</td>
            <td><span class="pill pass">INFO</span></td>
          </tr>
          <tr>
            <td>Checks Exitosos</td>
            <td>{checks_pass}</td>
            <td><span class="pill pass">OK</span></td>
          </tr>
          <tr>
            <td>Checks Fallidos</td>
            <td>{checks_fail}</td>
            <td><span class="pill {"fail" if checks_fail else "pass"}">{"FAIL" if checks_fail else "OK"}</span></td>
          </tr>
          <tr>
            <td>Duración Promedio</td>
            <td>{avg_duration}</td>
            <td><span class="pill pass">INFO</span></td>
          </tr>
          <tr>
            <td>P90</td>
            <td>{p90_duration}</td>
            <td><span class="pill pass">INFO</span></td>
          </tr>
          <tr>
            <td>P95</td>
            <td>{p95_duration}</td>
            <td><span class="pill pass">INFO</span></td>
          </tr>
          <tr>
            <td>Error Rate</td>
            <td>{http_failed}</td>
            <td><span class="pill {status_class}">{status}</span></td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="section">
      <h2>Detalle Técnico</h2>
      <details>
        <summary>Ver JSON completo</summary>
        <pre>{json.dumps(data, indent=2, ensure_ascii=False)}</pre>
      </details>
    </div>

    <div class="footer">
      Reporte generado automáticamente por GitHub Actions + k6
    </div>
  </div>
</body>
</html>
"""

with open(html_file, "w", encoding="utf-8") as f:
    f.write(html)

print(f"HTML generado: {html_file}")