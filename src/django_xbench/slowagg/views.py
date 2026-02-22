from django.http import JsonResponse, HttpResponseForbidden, HttpResponse
from django.conf import settings
from django.views.decorators.http import require_GET
from html import escape

from . import WINDOW


def _is_allowed(request):
    """
    Access control for the slow aggregation endpoint.

    This endpoint exposes internal performance metrics.
    Recommended defaults:
      - allow in DEBUG, OR
      - allow only staff/superuser in production
    """
    if settings.DEBUG:
        return True

    user = getattr(request, "user", None)
    return bool(user and user.is_authenticated and (user.is_staff or user.is_superuser))


@require_GET
def slowagg_snapshot(request):
    """
    Return a JSON snapshot of the rolling slow-endpoint aggregation.

    Usage:
      GET /__xbench__/slow/?n=20

    Notes:
      - Results are collected in-memory per process.
      - Do not expose publicly without authentication.
    """
    if not _is_allowed(request):
        return HttpResponseForbidden("xbench slow aggregation access denied")

    try:
        n = int(request.GET.get("n", "20"))
    except ValueError:
        n = 20
    n = max(1, min(n, 200))

    return JsonResponse(WINDOW.snapshot(n=n), json_dumps_params={"ensure_ascii": False})




@require_GET
def slowagg_ui(request):
    if not _is_allowed(request):
        return HttpResponseForbidden("xbench slow aggregation access denied")

    try:
        n = int(request.GET.get("n", "20"))
    except ValueError:
        n = 20
    n = max(1, min(n, 200))

    snap = WINDOW.snapshot(n=n)
    rows = snap["top"]

    html_rows = []
    for i, r in enumerate(rows, start=1):
        endpoint_html = escape(str(r["endpoint"]), quote=True)
        html_rows.append(
            "<tr>"
            f"<td class='rank'>{i}</td>"
            f"<td class='endpoint'><code>{endpoint_html}</code></td>"
            f"<td class='num'>{r['count']}</td>"
            f"<td class='num'>{r['avg']*1000:.2f} ms</td>"
            f"<td class='num'>{r['max']*1000:.2f} ms</td>"
            f"<td class='num'>{r['db_ratio']*100:.1f}%</td>"
            f"<td class='num'>{r['avg_q']:.1f}</td>"
            f"<td class='num'>{r['damage']:.3f} s</td>"
            "</tr>"
        )


    body = "\n".join(html_rows) if html_rows else "<tr><td colspan='8'>No data yet</td></tr>"

    style = """
    <style>
    body { font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial; padding: 24px; }
    h1 { margin: 0 0 12px 0; }
    .meta { color: #666; margin-bottom: 16px; }

    table { border-collapse: collapse; width: 100%; table-layout: fixed; }
    th, td { border-bottom: 1px solid #eee; padding: 10px 8px; vertical-align: middle; }
    thead th { background: #fafafa; font-weight: 700; }

    th.rank, td.rank { width: 56px; text-align: right; }
    th.endpoint, td.endpoint { width: 44%; text-align: left; }
    th.num, td.num { text-align: right; font-variant-numeric: tabular-nums; }

    td.endpoint { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

    code { background: #f3f3f3; padding: 2px 6px; border-radius: 6px; }
    </style>
    """.strip()

    html = (
        "<!doctype html>\n"
        "<html>\n"
        "<head>\n"
        "  <meta charset='utf-8' />\n"
        "  <title>django-xbench: Slow Endpoints</title>\n"
        f"  {style}\n"
        "</head>\n"
        "<body>\n"
        f"  <h1>Slow Endpoints (Top {n})</h1>\n"
        "  <div class='meta'>\n"
        f"    window={snap['window_seconds']}s, bucket={snap['bucket_seconds']}s × {snap['bucket_count']} | "
        f"generated_at={snap['generated_at']}\n"
        "  </div>\n"
        "\n"
        "  <table>\n"
        "    <colgroup>\n"
        "      <col style='width:56px'>\n"
        "      <col style='width:44%'>\n"
        "      <col style='width:10%'>\n"
        "      <col style='width:12%'>\n"
        "      <col style='width:12%'>\n"
        "      <col style='width:8%'>\n"
        "      <col style='width:8%'>\n"
        "      <col style='width:10%'>\n"
        "    </colgroup>\n"
        "    <thead>\n"
        "      <tr>\n"
        "        <th class='rank'>#</th>\n"
        "        <th class='endpoint'>Endpoint</th>\n"
        "        <th class='num'>Count</th>\n"
        "        <th class='num'>Avg</th>\n"
        "        <th class='num'>Max</th>\n"
        "        <th class='num'>DB%</th>\n"
        "        <th class='num'>Avg Q</th>\n"
        "        <th class='num'>Damage</th>\n"
        "      </tr>\n"
        "    </thead>\n"
        "    <tbody>\n"
        f"{body}\n"
        "    </tbody>\n"
        "  </table>\n"
        "</body>\n"
        "</html>\n"
    )

    return HttpResponse(html)
