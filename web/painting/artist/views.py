from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.conf import settings
from PIL import Image
import numpy as np
import os
from artist.ai_model import extract_features, predict
from django.http import JsonResponse


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

  return render(request, 'artist/result.html', {'img_url': img_url, 'pred':prediction})
