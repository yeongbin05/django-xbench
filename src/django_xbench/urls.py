from django.urls import include, path

urlpatterns = [
    # XBench developer endpoints (do not expose publicly without auth)
    path("__xbench__/", include("django_xbench.slowagg.urls")),
]
