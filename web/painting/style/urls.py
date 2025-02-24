from django.urls import path
import style.views

app_name = 'style'

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
  path('',style.views.search, name='search'),
  path('result/', style.views.result, name='result'),
  # path('output/', style.views.output, name='output'),
]

# 개발 환경에서 미디어 파일 서빙
if settings.DEBUG:
  urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)