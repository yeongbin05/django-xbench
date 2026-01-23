import contextvars

db_duration_ctx = contextvars.ContextVar("db_duration_ctx", default=0.0)
db_queries_ctx = contextvars.ContextVar("db_queries_ctx", default=0)
