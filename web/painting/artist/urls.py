from django.urls import path
import artist.views

app_name = 'artist'

urlpatterns = [
  path('',artist.views.search, name='search'),
  path('result/', artist.views.result, name='result'),
  # path('output/', artist.views.output, name='output'),
]