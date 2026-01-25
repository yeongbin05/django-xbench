from time import perf_counter
from django.http import JsonResponse
from django.db import connection


def db_heavy(request):
    # Intentionally generate multiple DB queries
    with connection.cursor() as cur:
        for _ in range(30):
            cur.execute("SELECT 1")
            cur.fetchone()

    return JsonResponse({"ok": True, "type": "db-heavy"})


def app_heavy(request):
    # Intentionally consume CPU time (simulate app bottleneck)
    start = perf_counter()
    while perf_counter() - start < 0.05:  # 50ms
        pass

    return JsonResponse({"ok": True, "type": "app-heavy"})
