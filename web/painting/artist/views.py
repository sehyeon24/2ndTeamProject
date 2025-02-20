from django.shortcuts import render
from django.core.files.base import ContentFile
from django.http import HttpResponseRedirect
from django.urls import reverse

# Create your views here.
def search(request):
  if request.method == 'POST' and request.FILES['image']:
    uploaded_file = request.FILES['image']

    # 이미지 파일을 ContentFile로 변환하여 변수에 저장
    img = ContentFile(uploaded_file.read())

    # 이미지 변수를 result로 전송
    return HttpResponseRedirect(reverse('artist:result'), img)

  return render(request,
                template_name='artist/search.html')

def result(request, img):
  # Ai 예측하기 ㄱㄱ염
  # img => (128,128, 3) 파일로 만들기
  # img => 각자 확률 높은 모델 돌리기
  # 결과값 저장 후 리턴 pred
  pred = '반 고흐'

  return render(request,
                template_name='artist/result.html',
                context={'img':img, 'pred':pred})

