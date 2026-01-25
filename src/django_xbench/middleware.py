from time import perf_counter
from contextlib import ExitStack
from django.db import connections
import logging

from .context import db_duration_ctx, db_queries_ctx
from .db import instrument_cursor
from .conf import XBENCH_LOG_ENABLED, XBENCH_LOG_LEVEL

logger = logging.getLogger("django_xbench")


class XBenchMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        token_dur = db_duration_ctx.set(0.0)
        token_q = db_queries_ctx.set(0)
        start = perf_counter()

        try:
            with ExitStack() as stack:
                for conn in connections.all():
                    stack.enter_context(conn.execute_wrapper(instrument_cursor))
                response = self.get_response(request)

            total = perf_counter() - start
            db_time = db_duration_ctx.get()
            q_count = db_queries_ctx.get()
            app_time = max(0.0, total - db_time)

            # ---- Server-Timing header ----
            existing = response.get("Server-Timing")

            mine = (
                f"total;dur={total*1000:.3f}, "
                f"db;dur={db_time*1000:.3f}, "
                f"app;dur={app_time*1000:.3f}"
            )

            response["Server-Timing"] = f"{existing}, {mine}" if existing else mine


            # ---- Query count header (recommended) ----
            response["X-Bench-Queries"] = str(q_count)


            # ---- Log Option ----
            if XBENCH_LOG_ENABLED:
                msg = (
                    f"[XBENCH] {request.method} {request.path} | "
                    f"total={total*1000:.3f}ms "
                    f"db={db_time*1000:.3f}ms "
                    f"app={app_time*1000:.3f}ms "
                    f"q={q_count}"
                )

                if XBENCH_LOG_LEVEL == "debug":
                    logger.debug(msg)
                else:
                    logger.info(msg)

            return response

        finally:
            db_duration_ctx.reset(token_dur)
            db_queries_ctx.reset(token_q)
