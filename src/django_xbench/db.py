from time import perf_counter
from .context import db_duration_ctx, db_queries_ctx

def instrument_cursor(execute, sql, params, many, context):
    start_time = perf_counter()
    try:
        return execute(sql, params, many, context)
    finally:
        dur = perf_counter() - start_time
        db_duration_ctx.set(db_duration_ctx.get() + dur)
        db_queries_ctx.set(db_queries_ctx.get() + 1)
