import http from 'k6/http';
import { check, sleep } from 'k6';

const BASE_URL = __ENV.BASE_URL || 'https://ungovernably-poachier-rochell.ngrok-free.dev/health';

export const options = {
  vus: 10,
  duration: '30s',
};

export default function () {
  const res = http.get(`${BASE_URL}`);

  check(res, {
    'status es 200': (r) => r.status === 200,
  });

  sleep(1);
}

// 🚨 versión SEGURA (sin htmlReport)
export function handleSummary(data) {
  const now = new Date();
  const timestamp = now.toISOString().replace(/[:.]/g, '-');

  return {
    [`report_gitactions/summary-${timestamp}.json`]: JSON.stringify(data, null, 2),
  };
}