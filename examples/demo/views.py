from time import perf_counter
from django.http import JsonResponse
from django.db import connection


def db_heavy(request):
    # 일부러 DB 쿼리 여러 번 발생
    with connection.cursor() as cur:
        for _ in range(30):
            cur.execute("SELECT 1")
            cur.fetchone()

    return JsonResponse({"ok": True, "type": "db-heavy"})


def app_heavy(request):
    # 일부러 CPU 바쁘게 만들기 (WAS 시간 증가)
    start = perf_counter()
    while perf_counter() - start < 0.05:  # 50ms
        pass

    return JsonResponse({"ok": True, "type": "app-heavy"})
