# Backend API Load Testing (k6)

Simple load test script using [k6](https://k6.io/) to test the FastAPI guestbook backend and trigger HPA autoscaling.

---

## 🚀 How to Run (Triggers HPA in < 2 mins)

### In-Cluster Execution (Recommended)
This runs k6 inside the cluster as an ephemeral pod. Requests hit `http://backend:8000`, automatically distributing load across **all** backend pods:

**In Git Bash / Linux / macOS:**
```bash
cat loadtesting/script.js | kubectl run k6-test-$RANDOM --rm -i --image=grafana/k6:latest -n fluid-ai --restart=Never --command -- k6 run -
```

**In Windows PowerShell:**
```powershell
Get-Content loadtesting/script.js | kubectl run "k6-test-$(Get-Random)" --rm -i --image=grafana/k6:latest -n fluid-ai --restart=Never --command -- k6 run -
```

*Note: The `--rm` flag automatically deletes the pod as soon as k6 finishes. Using dynamic names (`$RANDOM`) prevents name collisions if re-running immediately.*

---

## ⚙️ Customizing Load

You can override the virtual users (`VUS`) and duration (`DURATION`):

```bash
cat loadtesting/script.js | kubectl run k6-test --rm -i --image=grafana/k6:latest -n fluid-ai --restart=Never --command -- k6 run -e VUS=50 -e DURATION=3m -
```

---

## 👀 Watching Autoscaling in Action

Open your k9s dashboard or run in another terminal:

```bash
# Watch HPA replica count and CPU utilization:
kubectl get hpa backend-hpa -n fluid-ai --watch

# View pod CPU metrics:
kubectl top pods -n fluid-ai
```
