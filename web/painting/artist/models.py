from django.db import models

# Create your models here.
class artist(models.Model): # 테이블명 : blog_post
  artis_no = models.AutoField(primary_key=True) # PK가 없을 경우 자동 생성
  name = models.CharField(max_length=100) # 최대 길이 반드시 지정 VARCHAR 타입
  desc = models.TextField() # 최대 길이 제한이 없음 CLOB, TEXT 타입