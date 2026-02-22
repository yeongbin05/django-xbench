from time import perf_counter
from contextlib import ExitStack
import logging

from django.db import connections
from django.urls import resolve, Resolver404

from .context import db_duration_ctx, db_queries_ctx
from .db import instrument_cursor
from .slowagg import WINDOW
from .conf import (
    XBENCH_ENABLED,
    XBENCH_LOG_ENABLED,
    XBENCH_LOG_LEVEL,
    XBENCH_SLOW_AGG_ENABLED,
)

logger = logging.getLogger("django_xbench")


class XBenchMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not XBENCH_ENABLED:
            return self.get_response(request)

        db_duration_token = db_duration_ctx.set(0.0)
        db_queries_token = db_queries_ctx.set(0)
        start = perf_counter()

        try:
            with ExitStack() as stack:
                for conn in connections.all():
                    stack.enter_context(conn.execute_wrapper(instrument_cursor))
                response = self.get_response(request)

            total = perf_counter() - start
            db_time = db_duration_ctx.get()
            query_count = db_queries_ctx.get()
            app_time = max(0.0, total - db_time)

            if XBENCH_SLOW_AGG_ENABLED:
                path = request.path_info.lstrip("/")
                if not (path.startswith("__xbench__/") or path.startswith(".well-known/")):
                    try:
                        match = resolve(request.path_info)
                        endpoint_key = match.route or request.path_info
                    except Resolver404:
                        endpoint_key = request.path_info

                    WINDOW.update(
                        endpoint_key,
                        duration_s=total,
                        db_s=db_time,
                        query_count=query_count,
                    )
            current_timing = response.get("Server-Timing")
            metrics = [
                f"xbench-total;dur={total * 1000:.3f}",
                f"xbench-db;dur={db_time * 1000:.3f}",
                f"xbench-app;dur={app_time * 1000:.3f}",
            ]
            xbench_metrics = ", ".join(metrics)

            if current_timing:
                current_timing = current_timing.strip().strip(",")
                response["Server-Timing"] = f"{current_timing}, {xbench_metrics}"
            else:
                response["Server-Timing"] = xbench_metrics

            response["X-Bench-Queries"] = str(query_count)

            if XBENCH_LOG_ENABLED:
                msg = (
                    f"[XBENCH] {request.method} {request.path} | "
                    f"xbench_total={total * 1000:.3f}ms "
                    f"xbench_db={db_time * 1000:.3f}ms "
                    f"xbench_app={app_time * 1000:.3f}ms "
                    f"q={query_count}"
                )
                if XBENCH_LOG_LEVEL == "debug":
                    logger.debug(msg)
                else:
                    logger.info(msg)

            return response

        finally:
            db_duration_ctx.reset(db_duration_token)
            db_queries_ctx.reset(db_queries_token)
