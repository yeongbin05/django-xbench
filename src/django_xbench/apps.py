from django.apps import AppConfig

class DjangoXBenchConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "django_xbench"
    verbose_name = "Django X-Bench"  # 관리자 페이지 등에서 보일 이쁜 이름