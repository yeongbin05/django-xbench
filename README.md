# django-xbench

Here's how django-xbench exposes request timing breakdown using the Server-Timing header:
![Server Timing Preview](https://raw.githubusercontent.com/yeongbin05/django-xbench/master/docs/server-timing.PNG)

Measure Django request time breakdown (**total / db / app**) and query count with minimal setup.  
Adds `Server-Timing` and `X-Bench-Queries` headers and optionally logs per-request metrics.

> Goal: make performance debugging “visible” (DB vs app/serialization) without heavyweight APM.

## Features

- ✅ Measures total request time and DB time (via `connection.execute_wrapper`)
- ✅ Calculates app time (= total - db)
- ✅ Counts DB queries
- ✅ Adds response headers:
  - `Server-Timing: xbench-total;dur=..., xbench-db;dur=..., xbench-app;dur=...`
  - `X-Bench-Queries: <int>`
- ✅ Optional logging:
  - `[XBENCH] GET /path | xbench_total=...ms xbench_db=...ms xbench_app=...ms q=...`
- ✅ Tested with `pytest` + `pytest-django`

## Installation


```bash
pip install django-xbench
```

For local development (recommended):

```bash
pip install -e ".[dev]"
```

## Quickstart

1) Add middleware in your `settings.py`:

```py
MIDDLEWARE = [
    # Recommended: place near the top to approximate end-to-end server time
    # (includes other middleware overhead).
    "django_xbench.middleware.XBenchMiddleware",

    # ... other middleware ...

    # Optional: place near the bottom to focus on view/serializer/template time.
    # (Excludes middleware above XBench; includes anything below it.)
]

```

2) Run your server and hit any endpoint:

**In your project:**
```bash
python manage.py runserver
curl -I http://127.0.0.1:8000/<your-endpoint>/

```
**In this repo (demo):**
```bash
python -m examples.manage runserver
curl -I http://127.0.0.1:8000/db-heavy/
```
You should see headers similar to:

```text
Server-Timing: xbench-total;dur=12.345, xbench-db;dur=1.234, xbench-app;dur=11.111
X-Bench-Queries: 3
```

## Output

### Server-Timing

Example:

```text
Server-Timing: xbench-total;dur=52.300, xbench-db;dur=14.100, xbench-app;dur=38.200
```

- `xbench-total`: whole request duration
- `xbench-db`: total DB time measured by wrapper
- `xbench-app`: `max(0, total - db)` (serialization/template/python time etc.)

You can inspect this in Chrome DevTools → Network → Timing  
(or any browser that supports the Server-Timing spec).


### Query count header

```text
X-Bench-Queries: 5
```

## Configuration

You can configure XBench via `settings.py` or Environment Variables.

**settings.py:**
```python
XBENCH_LOG_ENABLED = True
XBENCH_LOG_LEVEL = "debug"  # default: "info"
```

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

> Note: this repo includes a bundled `examples/` Django project used by `pytest-django`.
> The provided `pytest.ini` config sets `pythonpath = .` so `examples` can be imported reliably.

If you want to see logs while testing:

```bash
pytest -s
```

### Demo project (bundled)

This repository includes an `examples/` Django project for manual testing.

Run it from the repository root:

```bash
python -m examples.manage runserver
```

Try a few endpoints:

```bash
curl -I http://127.0.0.1:8000/db-heavy/
curl -I http://127.0.0.1:8000/app-heavy/
curl -I http://127.0.0.1:8000/admin/login/
```

## Compatibility

- Python: 3.9+
- Django: 3.2+ (tested on Django 5.2.x)


## Roadmap

- [ ] DRF serialization time breakdown (view/serializer timing)
- [ ] More robust `Server-Timing` merging (preserve existing metrics)
- [ ] Docs: real-world examples (N+1 detection demo endpoints)
- [ ] CI (GitHub Actions) for tests & release

## Contributing

Issues and PRs are welcome.  
If you propose new metrics, please include:

- minimal reproducible example
- tests
- documentation update

## License

MIT
