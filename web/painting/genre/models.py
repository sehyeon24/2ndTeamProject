from django.db import models

# Create your models here.
class genre(models.Model): # 테이블명 : blog_post
  genre_no = models.AutoField(primary_key=True) # PK가 없을 경우 자동 생성
  genre = models.CharField(max_length=100,unique=True) # 최대 길이 반드시 지정 VARCHAR 타입
  desc = models.TextField(blank=True,null=True) # 최대 길이 제한이 없음 CLOB, TEXT 타입