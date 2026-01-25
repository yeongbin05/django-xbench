import pytest
from django.urls import path
from django.http import JsonResponse
from django.db import connection


def test_server_timing_header(client, settings):

    def view(request):
        return JsonResponse({"ok": True})

    settings.ROOT_URLCONF = type(
        "TmpUrls",
        (),
        {"urlpatterns": [path("ping/", view)]},
    )

    res = client.get("/ping/")

    assert "Server-Timing" in res.headers

@pytest.mark.django_db
def test_query_count_header(client, settings):

    def view(request):
        with connection.cursor() as cur:
            cur.execute("SELECT 1")
        return JsonResponse({"ok": True})

    settings.ROOT_URLCONF = type(
        "TmpUrls",
        (),
        {"urlpatterns": [path("db/", view)]},
    )

    res = client.get("/db/")

    assert int(res.headers["X-Bench-Queries"]) >= 1
