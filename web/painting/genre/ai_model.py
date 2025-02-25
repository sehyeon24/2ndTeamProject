import os
import numpy as np
import joblib  # joblib 라이브러리로 모델 로딩
from tensorflow.keras.applications import VGG16
from tensorflow.keras.models import Model
from django.conf import settings
from PIL import Image
import tensorflow as tf

# VGG16 모델 로드 (Feature Extractor)
base_model = VGG16(weights="imagenet", include_top=False, input_shape=(128, 128, 3))
model = Model(inputs=base_model.input, outputs=tf.keras.layers.GlobalAveragePooling2D()(base_model.output))

# 학습된 Keras 모델 로드 (예시로 model.h5 파일 사용)
MODEL_PATH = os.path.join(settings.BASE_DIR, "model", "genre_rf.joblib")
LABEL_PATH = os.path.join(settings.BASE_DIR, "model", "genre_label.pkl")
xgb_model = joblib.load(MODEL_PATH)
le = joblib.load(LABEL_PATH)

def extract_features(full_img_path):
  """
  이미지 경로를 받아서 VGG16 모델을 사용해 특징 벡터를 추출하는 함수
  """

  try:
    img = Image.open(full_img_path).convert("RGB")  # RGB 변환 (혹시모를 오류 방지)
    img_array = np.array(img, dtype=np.float32)
    img_array = np.expand_dims(img_array, axis=0)  # 배치 차원 추가 (1, 128, 128, 3)

    features = model.predict(img_array, verbose=0)  # 특징 벡터 추출
    return features

  except Exception as e:
    print(f"Error processing image {full_img_path}: {e}")
    return None


def predict(features):
  """
  추출된 특징 벡터를 받아서 학습된 Keras 모델로 예측하는 함수
  """
  try:
    prediction = xgb_model.predict(features)  # 특징 벡터를 모델에 입력
    prediction = le.inverse_transform(prediction)
    return prediction[0]  # 예측된 클래스 반환
  except Exception as e:
    print(f"Prediction error: {e}")
    return None