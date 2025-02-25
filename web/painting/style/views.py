from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.conf import settings
from PIL import Image
import os
from style.ai_model import extract_features, predict
from django.http import JsonResponse
import requests
from bs4 import BeautifulSoup


def search(request):
  if request.method == 'POST' and request.FILES.get('image'):
    uploaded_file = request.FILES['image']

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

    return HttpResponseRedirect(reverse('style:result'))

  return render(request, 'style/search.html')

def result(request):
  img_path = request.session.get('uploaded_image_path', None)

  if not img_path:
    return HttpResponseRedirect(reverse('style:search'))  # 이미지 없으면 검색 페이지로

  # MEDIA_URL을 사용하여 웹에서 접근 가능한 이미지 URL 생성
  img_url = f"{settings.MEDIA_URL}{img_path}"

  # img_path를 절대 경로로 변경
  full_img_path = os.path.join(settings.MEDIA_ROOT, img_path)

  features = extract_features(full_img_path)  # 특징 벡터 추출

  if features is None:
    return JsonResponse({"error": "Feature extraction failed"}, status=500)

  prediction = predict(features)  # 예측 수행
  prediction = prediction.replace('_', ' ')

  if prediction is None:
    return JsonResponse({"error": "Prediction failed"}, status=500)

  url = "https://en.wikipedia.org/wiki/" + prediction
  response = requests.get(url)

  # 응답이 정상인지 확인
  if response.status_code == 200:
    soup = BeautifulSoup(response.text, "html.parser")
    style_html = soup.find('div', class_="mw-content-ltr mw-parser-output")
    style_html = style_html.find('p').text if style_html else "<p>정보를 가져올 수 없습니다.</p>"
  else:
    style_html = "정보를 가져올 수 없습니다."

  return render(request, 'style/result.html', {'img_url': img_url, 'pred':prediction, 'style_html':style_html})
