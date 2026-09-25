import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  vus: __ENV.VUS ? parseInt(__ENV.VUS) : 40,
  duration: __ENV.DURATION || '5m',
};

// Auto-detect: if running inside a K8s pod use internal service, otherwise localhost
const defaultTarget = __ENV.KUBERNETES_SERVICE_HOST ? 'http://backend:8000' : 'http://localhost:8000';
const targets = (__ENV.TARGET_URL || defaultTarget).split(',').map((u) => u.trim());

export default function () {
  const BASE_URL = targets[__VU % targets.length];

  // 1. Health check
  const healthRes = http.get(`${BASE_URL}/health`);
  check(healthRes, {
    'health status is 200': (r) => r.status === 200,
  });

  // 2. Add name
  const payload = JSON.stringify({ name: `user-${__VU}-${Date.now()}` });
  const headers = { 'Content-Type': 'application/json' };
  const addNameRes = http.post(`${BASE_URL}/name`, payload, { headers });
  check(addNameRes, {
    'add name status is 201': (r) => r.status === 201,
  });

  // 3. Get names
  const getNamesRes = http.get(`${BASE_URL}/names`);
  check(getNamesRes, {
    'get names status is 200': (r) => r.status === 200,
  });

  // 4. Pacing
  sleep(0.05);
}
