from django.urls import path
from .views import upload_video
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", upload_video, name="upload_video"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

