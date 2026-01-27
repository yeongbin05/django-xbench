from django.conf import settings


def get_setting(name, default):
    return getattr(settings, name, default)


XBENCH_ENABLED = get_setting("XBENCH_ENABLED", True)
XBENCH_LOG_ENABLED = get_setting("XBENCH_LOG_ENABLED", False)
XBENCH_LOG_LEVEL = str(get_setting("XBENCH_LOG_LEVEL", "info")).lower()
