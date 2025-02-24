from django.urls import path
import artist.views

app_name = 'artist'

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
  path('',artist.views.search, name='search'),
  path('result/', artist.views.result, name='result'),
  # path('output/', artist.views.output, name='output'),
]

# 개발 환경에서 미디어 파일 서빙
if settings.DEBUG:
  urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
  
  
