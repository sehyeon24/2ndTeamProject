from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.conf import settings
from PIL import Image
import numpy as np
import os
from artist.ai_model import extract_features, predict
from django.http import JsonResponse
import requests
from bs4 import BeautifulSoup


def search(request):
  if request.method == 'POST' and request.FILES.get('image'):
    uploaded_file = request.FILES['image']


    import os

    # 'uploads' 폴더가 없으면 생성
    uploads_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
    if not os.path.exists(uploads_dir):
      os.makedirs(uploads_dir)  # 'uploads' 폴더 생성

    # 파일 저장 경로 설정 (MEDIA_ROOT 내부)
    file_name = f"uploads/{uploaded_file.name}"
    file_path = os.path.join(settings.MEDIA_ROOT, file_name)

    # 이미지 열고 리사이즈 후 저장
    img = Image.open(uploaded_file)
    img = img.resize((128, 128))
    img.save(file_path)

    # 세션에 '웹에서 접근 가능한' 상대 경로 저장 (MEDIA_URL 기준)
    request.session['uploaded_image_path'] = file_name  # 'uploads/파일명.jpg'

    return HttpResponseRedirect(reverse('artist:result'))

  return render(request, 'artist/search.html')

def result(request):
  img_path = request.session.get('uploaded_image_path', None)

  if not img_path:
    return HttpResponseRedirect(reverse('artist:search'))  # 이미지 없으면 검색 페이지로

  # MEDIA_URL을 사용하여 웹에서 접근 가능한 이미지 URL 생성
  img_url = f"{settings.MEDIA_URL}{img_path}"

  # img_path를 절대 경로로 변경
  full_img_path = os.path.join(settings.MEDIA_ROOT, img_path)

  features = extract_features(full_img_path)  # 특징 벡터 추출

  if features is None:
    return JsonResponse({"error": "Feature extraction failed"}, status=500)

  prediction = predict(features)  # 예측 수행

  if prediction is None:
    return JsonResponse({"error": "Prediction failed"}, status=500)

  url = "https://www.wikiart.org/en/"+prediction
  response = requests.get(url)

  # 응답이 정상인지 확인
  if response.status_code == 200:
    soup = BeautifulSoup(response.text, "html.parser")

    # <article> 태그 가져오기
    article = soup.find("article")

    if article:
      # 특정 클래스를 가진 <li> 요소 제거
      for li in article.find_all("li", class_="order-reproduction"):
        li.decompose()  # 해당 요소 삭제

      for li in soup.find_all("li"):
        for a_tag in li.find_all('a'):
          if a_tag and not a_tag["href"].startswith("http"):
            a_tag.unwrap()  # <a> 태그를 제거하고 내부 텍스트만 유지

      # 변경된 HTML을 문자열로 변환
      artist_html = str(article)

    else:
      artist_html = "<p>정보를 가져올 수 없습니다.</p>"


  return render(request, 'artist/result.html', {'img_url': img_url, "artist_html": artist_html})