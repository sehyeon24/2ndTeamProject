from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.conf import settings
from PIL import Image
import os
from genre.ai_model import extract_features, predict
from django.http import JsonResponse
import requests
from bs4 import BeautifulSoup

# 리스트를 group_size 개씩 묶어서 반환하는 함수
def group_list(data, group_size):
  return [data[i:i + group_size] for i in range(0, len(data), group_size)]

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

    return HttpResponseRedirect(reverse('genre:result'))

  return render(request, 'genre/search.html')

def result(request):
  img_path = request.session.get('uploaded_image_path', None)

  if not img_path:
    return HttpResponseRedirect(reverse('genre:search'))  # 이미지 없으면 검색 페이지로

  # MEDIA_URL을 사용하여 웹에서 접근 가능한 이미지 URL 생성
  img_url = f"{settings.MEDIA_URL}{img_path}"

  # img_path를 절대 경로로 변경
  full_img_path = os.path.join(settings.MEDIA_ROOT, img_path)

  features = extract_features(full_img_path)  # 특징 벡터 추출

  if features is None:
    return JsonResponse({"error": "Feature extraction failed"}, status=500)

  prediction = predict(features)  # 예측 수행
  prediction = prediction.replace(' ', '-')

  if prediction  is None:
    return JsonResponse({"error": "Prediction failed"}, status=500)

  url = "https://www.wikiart.org/en/artists-by-genre/"+prediction
  response = requests.get(url)

  artist_data = []

  # 응답이 정상인지 확인
  if response.status_code == 200:
    soup = BeautifulSoup(response.text, "html.parser")

    # 태그 가져오기
    container = soup.find("div", class_="artist-gallery-outter-container")

    if container:
      # 이미지 제거
      for img in container.find_all("img"):
        img.decompose()

      # 이름 링크 제거 (a 태그를 없애고 내부 텍스트 유지)
      for a in container.find_all("a"):
        a.unwrap()

      # 페이지 이동 버튼 제거
      load_more_button = container.find("div", class_="masonry-load-more-button-wrapper")
      if load_more_button:
        load_more_button.decompose()

      artists = container.find_all("li")  # 각 아티스트 리스트

      for artist in artists:
        name_tag = artist.find("div", class_="artist-name")
        info_tag = artist.find("div", class_="artist-short-info")
        count_tag = artist.find("div", class_="works-count")

        # 이름, 정보, 작품 수 추출
        name = name_tag.text.strip() if name_tag else "Unknown"
        info = info_tag.text.strip() if info_tag else "No info"
        count = count_tag.text.strip() if count_tag else "0 artworks"

        # 리스트에 추가
        artist_data.append({"name": name, "info": info, "count": count})

    # 3개씩 그룹화
    group_artists = group_list(artist_data, 3)

  else:
    group_artists  = "<p>정보를 가져올 수 없습니다.</p>"

  return render(request, 'genre/result.html', {'img_url': img_url, "group_artists": group_artists, "pred": prediction})
