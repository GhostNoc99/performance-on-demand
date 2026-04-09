import http from 'k6/http';
import { check, sleep } from 'k6';
import { htmlReport } from 'https://jslib.k6.io/k6-summary/0.1.0/index.js';

const BASE_URL = __ENV.BASE_URL || 'http://host.docker.internal:8000/health';

export const options = {
  vus: 1,
  duration: '10s',
};

export default function () {
  const res = http.get(`${BASE_URL}/health`);

  check(res, {
    'status es 200': (r) => r.status === 200,
    'responde en menos de 500ms': (r) => r.timings.duration < 500,
  });

  sleep(1);
}

export function handleSummary(data) {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');

  return {
    [`report_gitactions/reporte-${timestamp}.html`]: htmlReport(data),
    [`report_gitactions/reporte-${timestamp}.json`]: JSON.stringify(data, null, 2),
    stdout: 'Reporte generado en report_gitactions\n',
  };
}