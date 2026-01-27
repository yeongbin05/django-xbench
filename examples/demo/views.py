from time import sleep
from django.http import JsonResponse
from django.db import connections


def db_heavy(request):
    # Demo: deterministic DB workload (expected_queries=30)
    with connections["default"].cursor() as cur:
        for _ in range(30):
            cur.execute("SELECT 1")
            cur.fetchone()
    return JsonResponse({"ok": True, "type": "db-heavy", "expected_queries": 30})


def app_heavy(request):
    # Demo: deterministic non-DB latency (expected_queries=0)
    sleep(0.05)
    return JsonResponse({"ok": True, "type": "app-heavy", "expected_queries": 0})
