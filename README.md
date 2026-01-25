# django-xbench

Measure Django request time breakdown (**total / db / app**) and query count with minimal setup.  
Adds `Server-Timing` and `X-Bench-Queries` headers and optionally logs per-request metrics.

> Goal: make performance debugging “visible” (DB vs app/serialization) without heavyweight APM.

## Features

- ✅ Measures total request time and DB time (via `connection.execute_wrapper`)
- ✅ Calculates app time (= total - db)
- ✅ Counts DB queries
- ✅ Adds response headers:
  - `Server-Timing: total;dur=..., db;dur=..., app;dur=...`
  - `X-Bench-Queries: <int>`
- ✅ Optional logging:
  - `[XBENCH] GET /path | total=...ms db=...ms app=...ms q=...`
- ✅ Tested with `pytest` + `pytest-django`

## Installation

> **(WIP)** Once published on PyPI:

```bash
pip install django-xbench
```

For local development:

```bash
pip install -e .
```

## Quickstart

1) Add middleware in `settings.py`:

```py
MIDDLEWARE = [
    # ...
    "django_xbench.middleware.XBenchMiddleware",
]
```

2) Run server and hit any endpoint:

```bash
python manage.py runserver
curl -I http://localhost:8000/<your-endpoint>/
```

You should see headers similar to:

```text
Server-Timing: total;dur=12.345, db;dur=1.234, app;dur=11.111
X-Bench-Queries: 3
```

### Note about `/db/` in tests

`/db/` is **test-only** (temporary URLConf inside pytest) and does not exist in the demo server.  
Use your real endpoint (e.g. `db-heavy`, `admin/login/`, etc.) when testing with `curl`.

## Output

### Server-Timing

Example:

```text
Server-Timing: total;dur=52.300, db;dur=14.100, app;dur=38.200
```

- `total`: whole request duration
- `db`: total DB time measured by wrapper
- `app`: `max(0, total - db)` (serialization/template/python time etc.)

You can inspect this in Chrome DevTools → Network → (select request) → Timing.

### Query count header

```text
X-Bench-Queries: 5
```

## Configuration

Environment variables (or settings) used:

- `XBENCH_LOG_ENABLED` (default: `false`)
- `XBENCH_LOG_LEVEL` (default: `info`, allowed: `debug` / `info`)

Example (Windows):

```bat
set XBENCH_LOG_ENABLED=1
set XBENCH_LOG_LEVEL=debug
```

Example (macOS/Linux):

```bash
export XBENCH_LOG_ENABLED=1
export XBENCH_LOG_LEVEL=debug
```

## Development

### Run tests

```bash
pytest
```

If you want to see logs while testing:

```bash
pytest -s
```

### Demo project

This repository includes an `example/` Django project for manual testing.

```bash
cd example
python manage.py runserver
```

## Compatibility

- Python: 3.10+
- Django: 4.x / 5.x (tested on Django 5.2.x)

## Roadmap

- [ ] DRF serialization time breakdown (view/serializer timing)
- [ ] More robust `Server-Timing` merging (preserve existing metrics)
- [ ] Docs: real-world examples (N+1 detection demo endpoints)
- [ ] CI (GitHub Actions) + PyPI release

## Contributing

Issues and PRs are welcome.  
If you propose new metrics, please include:

- minimal reproducible example
- tests
- documentation update

## License

MIT
