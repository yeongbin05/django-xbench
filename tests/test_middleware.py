import pytest
from django.db import connection
from django.http import JsonResponse
from django.urls import path


def test_server_timing_header(client, settings):
    def view(request):
        return JsonResponse({"ok": True})

    settings.ROOT_URLCONF = type(
        "TmpUrls",
        (),
        {"urlpatterns": [path("ping/", view)]},
    )

    res = client.get("/ping/")

    # Should add Server-Timing header with xbench metrics.
    assert "Server-Timing" in res.headers
    assert "xbench-total" in res.headers["Server-Timing"]


@pytest.mark.django_db
def test_query_count_header(client, settings):
    def view(request):
        # Trigger at least one DB query.
        with connection.cursor() as cur:
            cur.execute("SELECT 1")
        return JsonResponse({"ok": True})

    settings.ROOT_URLCONF = type(
        "TmpUrls",
        (),
        {"urlpatterns": [path("db/", view)]},
    )

    res = client.get("/db/")

    # Should expose query count as an integer header.
    assert int(res.headers["X-Bench-Queries"]) >= 1


def test_server_timing_appends_when_already_present(client, settings):
    def view(request):
        res = JsonResponse({"ok": True})
        # Existing Server-Timing should not be overridden.
        res["Server-Timing"] = "cache;dur=12.3"
        return res

    settings.ROOT_URLCONF = type(
        "TmpUrls",
        (),
        {"urlpatterns": [path("append/", view)]},
    )

    res = client.get("/append/")
    timing = res.headers["Server-Timing"]

    assert "cache;dur=12.3" in timing
    assert "xbench-total" in timing
    assert "xbench-db" in timing
    assert "xbench-app" in timing

    # Ensure xbench metrics were appended after the existing entry.
    assert timing.index("cache") < timing.index("xbench-total")



@pytest.mark.django_db
def test_contextvars_are_reset_between_requests(client, settings):
    def view(request):
        with connection.cursor() as cur:
            cur.execute("SELECT 1")
        return JsonResponse({"ok": True})

    settings.ROOT_URLCONF = type(
        "TmpUrls",
        (),
        {"urlpatterns": [path("leak/", view)]},
    )

    # First request (has 1 query)
    res1 = client.get("/leak/")
    q1 = int(res1.headers["X-Bench-Queries"])

    # Second request (same endpoint, same 1 query)
    res2 = client.get("/leak/")
    q2 = int(res2.headers["X-Bench-Queries"])

    # Each request should be isolated
    assert q1 >= 1
    assert q2 >= 1

    # Should NOT accumulate (ex: 1 -> 2)
    assert abs(q2 - q1) <= 1
