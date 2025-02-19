from django.shortcuts import render

# Create your views here.
def search(request):
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

# def output(request):
#   pass