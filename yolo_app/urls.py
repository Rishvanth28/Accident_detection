from django.urls import path
from .views import upload_video, stream_video  # Import the streaming view
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", upload_video, name="upload_video"),
    path("stream/<str:filename>/", stream_video, name="stream_video"),  # ✅ Add this line
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
