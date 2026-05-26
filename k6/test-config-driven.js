import http from 'k6/http';
import { check, sleep } from 'k6';
import { textSummary } from "https://jslib.k6.io/k6-summary/0.0.1/index.js";

// Variables inyectadas por Jenkins
const URL           = __ENV.URL            || 'http://localhost:8000/health';
const METHOD        = __ENV.METHOD         || 'GET';
const TPS           = parseInt(__ENV.TPS)  || 8;
const DURATION      = __ENV.DURATION       || '10m';
const RAMP_UP       = parseInt(__ENV.RAMP_UP) || 60;
const P95_THRESHOLD = parseInt(__ENV.P95_THRESHOLD) || 2000;
const ERROR_RATE    = parseFloat(__ENV.ERROR_RATE)  || 0.01;
const PRE_ALLOC_VUS = parseInt(__ENV.PRE_ALLOC_VUS) || 24;
const SERVICE_NAME  = __ENV.SERVICE_NAME   || 'unknown-service';
const REPORT_NAME   = __ENV.REPORT_NAME    || 'config-driven-report.html';

// ================================================================
// OPCIONES — constant-arrival-rate + ramp-up
// ================================================================
export const options = {
    scenarios: {
        ramp_up: {
            executor:        'ramping-arrival-rate',
            startRate:       0,
            timeUnit:        '1s',
            preAllocatedVUs: PRE_ALLOC_VUS,
            stages: [
                { target: TPS, duration: `${RAMP_UP}s` },
            ],
        },
        carga_estandar: {
            executor:        'constant-arrival-rate',
            rate:            TPS,
            timeUnit:        '1s',
            duration:        DURATION,
            preAllocatedVUs: PRE_ALLOC_VUS,
            maxVUs:          PRE_ALLOC_VUS * 2,
            startTime:       `${RAMP_UP}s`,
        },
    },
    thresholds: {
        'http_req_duration{scenario:carga_estandar}': [
            { threshold: `p(95)<${P95_THRESHOLD}`, abortOnFail: true }
        ],
        'http_req_failed{scenario:carga_estandar}': [
            { threshold: `rate<${ERROR_RATE}`, abortOnFail: true }
        ],
    },
    summaryTrendStats: ['min', 'avg', 'med', 'max', 'p(50)', 'p(90)', 'p(95)', 'p(99)'],
    tags: {
        service_name: SERVICE_NAME,
        test_type:    'carga',
        standard:     'v2.0',
    },
};

// ================================================================
// ESCENARIO PRINCIPAL
// ================================================================
export default function () {
    const params = {
        headers: { 'Content-Type': 'application/json' },
        tags: { service_name: SERVICE_NAME, test_type: 'carga' },
    };

    const res = http.request(METHOD, URL, null, params);

    check(res, {
        'status 2xx':                    (r) => r.status >= 200 && r.status < 300,
        [`p95 < ${P95_THRESHOLD}ms`]:    (r) => r.timings.duration < P95_THRESHOLD,
    });
}

// ================================================================
// REPORTE — mismo formato JSON que dynamic-test.js
// para que k6Utils.qualityGate y parseMetrics funcionen igual
// ================================================================
export function handleSummary(data) {
    const jsonName = REPORT_NAME.replace('.html', '.json');

    const dur      = data.metrics.http_req_duration?.values || {};
    const errRate  = data.metrics.http_req_failed?.values?.rate || 0;
    const reqRate  = data.metrics.http_reqs?.values?.rate || 0;

    const estado   = errRate === 0 && dur['p(95)'] < P95_THRESHOLD ? '✅ PASS' : '❌ FAIL';

    const jsonData = {
        iterations: data.metrics.iterations?.values?.count || 0,
        reqRate:    reqRate,
        errorRate:  errRate,
        p50:        dur['p(50)'] || 0,
        p90:        dur['p(90)'] || 0,
        p95:        dur['p(95)'] || 0,
        p99:        dur['p(99)'] || 0,
        avg:        dur.avg      || 0,
        min:        dur.min      || 0,
        max:        dur.max      || 0,
        // Campos extra del config-driven
        tps_objetivo:   TPS,
        p95_threshold:  P95_THRESHOLD,
        service_name:   SERVICE_NAME,
        test_standard:  'v2.0',
        resultado:      estado,
    };

    return {
        [`k6/reports/${REPORT_NAME}`]: generarReporte(data, estado),
        [`k6/reports/${jsonName}`]:    JSON.stringify(jsonData, null, 2),
        stdout: textSummary(data, { indent: ' ', enableColors: true }),
    };
}

function generarReporte(data, estado) {
    const dur      = data.metrics.http_req_duration?.values || {};
    const errRate  = data.metrics.http_req_failed?.values?.rate || 0;
    const totalReqs = data.metrics.http_reqs?.values?.count || 0;
    const color    = estado.includes('PASS') ? '#27ae60' : '#e74c3c';

    return `<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>Config-Driven Report — ${SERVICE_NAME}</title>
  <style>
    body { font-family: Arial, sans-serif; background:#f0f2f5; padding:20px; color:#2c3e50; }
    .container { max-width:1000px; margin:auto; }
    .header { background:${color}; color:white; padding:25px; border-radius:10px; text-align:center; margin-bottom:20px; }
    .header h1 { font-size:24px; margin-bottom:5px; }
    .cards { display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin-bottom:20px; }
    .card { background:white; padding:18px; border-radius:10px; text-align:center; box-shadow:0 2px 8px rgba(0,0,0,0.08); }
    .card .value { font-size:26px; font-weight:bold; margin-bottom:4px; }
    .card .label { font-size:11px; color:#666; }
    .section { background:white; padding:20px; border-radius:10px; margin-bottom:20px; box-shadow:0 2px 8px rgba(0,0,0,0.08); }
    .section h2 { font-size:15px; margin-bottom:12px; border-bottom:2px solid #ecf0f1; padding-bottom:8px; }
    table { width:100%; border-collapse:collapse; font-size:13px; }
    th { background:#2c3e50; color:white; padding:10px; text-align:left; }
    td { padding:10px; border-bottom:1px solid #ecf0f1; }
    .footer { background:#2c3e50; color:white; padding:14px; border-radius:10px; text-align:center; font-size:12px; }
  </style>
</head>
<body>
<div class="container">
  <div class="header">
    <h1>${estado} — ${SERVICE_NAME}</h1>
    <p>Prueba de CARGA · Estándar v2.0 · TPS objetivo: ${TPS} · Duración: ${DURATION}</p>
    <p>${new Date().toLocaleString()}</p>
  </div>
  <div class="cards">
    <div class="card">
      <div class="value" style="color:#3498db">${TPS}</div>
      <div class="label">🎯 TPS Objetivo</div>
    </div>
    <div class="card">
      <div class="value" style="color:${(dur['p(95)']||0) < P95_THRESHOLD ? '#27ae60':'#e74c3c'}">${(dur['p(95)']||0).toFixed(0)}ms</div>
      <div class="label">📊 P95 Real</div>
    </div>
    <div class="card">
      <div class="value" style="color:#9b59b6">${P95_THRESHOLD}ms</div>
      <div class="label">📏 P95 Umbral</div>
    </div>
    <div class="card">
      <div class="value" style="color:${errRate===0?'#27ae60':'#e74c3c'}">${(errRate*100).toFixed(2)}%</div>
      <div class="label">❌ Error Rate</div>
    </div>
  </div>
  <div class="section">
    <h2>📋 Resultados vs Estándar v2.0</h2>
    <table>
      <tr><th>Métrica</th><th>Valor obtenido</th><th>Umbral estándar</th><th>Estado</th></tr>
      <tr>
        <td>P95 Latencia</td>
        <td>${(dur['p(95)']||0).toFixed(0)}ms</td>
        <td>≤ ${P95_THRESHOLD}ms</td>
        <td>${(dur['p(95)']||0) < P95_THRESHOLD ? '✅ PASS' : '❌ FAIL'}</td>
      </tr>
      <tr>
        <td>Error Rate</td>
        <td>${(errRate*100).toFixed(2)}%</td>
        <td>< 1%</td>
        <td>${errRate < 0.01 ? '✅ PASS' : '❌ FAIL'}</td>
      </tr>
      <tr>
        <td>Total Requests</td>
        <td>${totalReqs}</td>
        <td>—</td>
        <td>📊 Info</td>
      </tr>
      <tr>
        <td>P99</td>
        <td>${(dur['p(99)']||0).toFixed(0)}ms</td>
        <td>—</td>
        <td>📊 Info</td>
      </tr>
    </table>
  </div>
  <div class="footer">
    ⚙️ Config-Driven Performance · ${SERVICE_NAME} · Estándar v2.0 · ${new Date().toLocaleString()}
  </div>
</div>
</body>
</html>`;
}