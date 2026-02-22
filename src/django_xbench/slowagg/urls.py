from django.urls import path

from .views import slowagg_snapshot,slowagg_ui

urlpatterns = [
    # Slow endpoint aggregation snapshot (JSON)
    # Example: GET /__xbench__/slow/?n=20
    path("slow/", slowagg_snapshot, name="xbench-slowagg"),
    path("slow/ui/", slowagg_ui, name="xbench-slowagg-ui"),
]
