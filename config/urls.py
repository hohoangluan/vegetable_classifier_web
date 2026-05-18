"""Root URL configuration for the VeggiClassify demo."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.pages.urls")),
    path("classify/", include("apps.classifier.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    # Phục vụ file từ thư mục dataset ngoài dự án
    import os
    from django.views.static import serve
    dataset_root = os.path.join(settings.BASE_DIR.parent, "dataset")
    urlpatterns += [
        path("dataset-media/<path:path>", serve, {"document_root": dataset_root}),
    ]
