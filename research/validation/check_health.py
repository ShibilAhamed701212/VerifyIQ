import os, json

os.environ["GEMINI_API_KEY"] = "test_key"
os.environ["VERIFYIQ_MODE"] = "demo"

from code.v2.startup_validator import StartupValidator

v = StartupValidator()
chk = v.validate_vision_availability()
print(f"DEMO mode: status={chk['status']}, detail={chk['detail'][:100]}")

os.environ["VERIFYIQ_MODE"] = "production"
v2 = StartupValidator()
chk2 = v2.validate_vision_availability()
print(f"PROD mode:  status={chk2['status']}, detail={chk2['detail'][:100]}")

full = v2.validate_all()
print(f"Full health ({full['status']}):")
for c in full['checks']:
    print(f"  {c['check']:25s}: {c['status']:6s} {c['detail'][:80]}")
