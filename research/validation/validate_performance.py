"""Performance benchmark: V1 vs V2 across claim volumes."""
import sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "code"))

from code.v2.pipeline import V2Pipeline
from code.v2.observability.metrics import get_collector

SAMPLE_CLAIM = "There is a dent on the rear bumper of my car"
SAMPLE_OBJECT = "car"
SAMPLE_USER = "benchmark_user"

def benchmark_v2(n: int) -> dict:
    get_collector().reset()
    pipe = V2Pipeline()
    start = time.time()
    for i in range(n):
        pipe.process(SAMPLE_CLAIM, [], SAMPLE_OBJECT, SAMPLE_USER)
    elapsed = time.time() - start
    metrics = get_collector().get_metrics()
    module_totals = {}
    for t in metrics.module_timings:
        module_totals[t.module] = module_totals.get(t.module, 0) + t.latency_ms
    return {
        "total_sec": round(elapsed, 4),
        "total_ms": round(elapsed * 1000, 2),
        "per_claim_ms": round((elapsed * 1000) / n, 4) if n > 0 else 0,
        "cps": round(n / elapsed, 1) if elapsed > 0 else float('inf'),
        "module_totals": module_totals,
        "module_avg": {k: round(v/n, 4) for k, v in module_totals.items()},
        "failures": len(metrics.model_failures),
    }

v2_r = {}
for n in [1, 10, 50]:
    print(f"V2: {n} claims...", flush=True)
    v2_r[n] = benchmark_v2(n)
    print(f"  {v2_r[n]['total_ms']}ms total, {v2_r[n]['per_claim_ms']}ms/claim", flush=True)

print("V1: 10 claims...", flush=True)
try:
    from config import Config
    from claim_processor import ClaimProcessor
    config = Config()
    proc = ClaimProcessor(config)
    row = {"user_id": SAMPLE_USER, "image_paths": "", "user_claim": SAMPLE_CLAIM, "claim_object": SAMPLE_OBJECT}
    start = time.time()
    for i in range(10):
        proc.process_claim(row)
    v1_elapsed = time.time() - start
    v1_ok = True
    v1pc = round((v1_elapsed * 1000) / 10, 4)
    print(f"  {round(v1_elapsed*1000,1)}ms total, {v1pc}ms/claim")
except Exception as e:
    v1_elapsed = 0
    v1_ok = False
    print(f"  V1 error: {e}")

L = []
L.append("# Performance Report — VerifyIQ V1 vs V2\n")
L.append("**Environment:** Windows, Python 3.12, no VLM API calls (degraded mode)\n")
L.append("**Sample:** \"" + SAMPLE_CLAIM + "\"\n")
L.append("## Overall Comparison\n")
L.append("| Metric | V1 (10) | V2 (1) | V2 (10) | V2 (50) |")
L.append("|---|---|---|---|---|")
if v1_ok:
    L.append(f"| Total (ms) | {round(v1_elapsed*1000,1)} | {v2_r[1]['total_ms']} | {v2_r[10]['total_ms']} | {v2_r[50]['total_ms']} |")
    L.append(f"| Per-claim (ms) | {v1pc} | {v2_r[1]['per_claim_ms']} | {v2_r[10]['per_claim_ms']} | {v2_r[50]['per_claim_ms']} |")
    L.append(f"| Claims/sec | {round(10/v1_elapsed,1)} | {v2_r[1]['cps']} | {v2_r[10]['cps']} | {v2_r[50]['cps']} |")
else:
    L.append("| Total (ms) | N/A | " + str(v2_r[1]['total_ms']) + " | " + str(v2_r[10]['total_ms']) + " | " + str(v2_r[50]['total_ms']) + " |")
L.append(f"| Failures | N/A | {v2_r[1]['failures']} | {v2_r[10]['failures']} | {v2_r[50]['failures']} |")

L.append("\n## V2 Module Breakdown (10 claims)\n")
r = v2_r[10]
L.append("| Module | Total (ms) | Avg (ms) | Share |")
L.append("|---|---|---|---|")
total_avg = sum(r['module_avg'].values()) or 1
for m in sorted(r['module_avg']):
    a = r['module_avg'][m]
    L.append(f"| {m} | {r['module_totals'].get(m,0):.2f} | {a:.4f} | {a/total_avg*100:.1f}% |")

L.append("\n## Module Scaling\n")
L.append("| Module | 1 claim (ms) | 10 claims | 50 claims |")
L.append("|---|---|---|---|")
all_mods = set()
for n in [1, 10, 50]:
    all_mods.update(v2_r[n]['module_avg'].keys())
for m in sorted(all_mods):
    vals = [f"{v2_r[n]['module_avg'].get(m,0):.4f}" for n in [1, 10, 50]]
    L.append(f"| {m} | {' | '.join(vals)} |")

L.append("\n## Scalability\n")
if v2_r.get(50) and v2_r[50]['total_ms'] > 0:
    L.append(f"- V2 (50 claims): {v2_r[50]['total_sec']}s = {v2_r[50]['per_claim_ms']}ms/claim")
    L.append(f"- Scale factor 1->10: {v2_r[10]['total_ms']/v2_r[1]['total_ms']:.1f}x (linear = ~10x)")
    L.append(f"- Scale factor 10->50: {v2_r[50]['total_ms']/v2_r[10]['total_ms']:.1f}x (linear = 5x)")
L.append("- Observation layer skipped (no API key); real VLM adds ~2-5s/claim\n")

L.append("## Projected Cost\n")
L.append("| Scenario | Cost/1000 claims |")
L.append("|---|---|")
L.append("| V2 without VLM | $0.00 |")
L.append("| V2 with Gemini Flash | ~$0.16-$0.40 |")
L.append("| V2 with 3 models | ~$0.50-$1.20 |")

with open(Path(__file__).parent / "PERFORMANCE_REPORT.md", "w") as f:
    f.write("\n".join(L))
print("Wrote PERFORMANCE_REPORT.md")
