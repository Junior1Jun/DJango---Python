from rest_framework import serializers
from .models import JSON_jeonmoon
from .models import JSON_hyeonhang
from .models import JSON_hangjeong

# serializers는 데이터셋을 JSON 또는 XML 형식의 데이터셋으로 변환해주는 클래스를 의미.

# 각 데이터셋(전문자료, 현행법령, 행정규칙)에 대해 JSON 형식의 데이터셋으로 변환해주는 클래스 정의.
# 각 클래스는 serializers.ModelSerializer 클래스를 상속받음.

class JSON_jeonmoon_Serializer(serializers.ModelSerializer):
    class Meta:
        model = JSON_jeonmoon         # JSON_jeonmoon 모델 사용
        fields = '__all__'            # 모든 필드 사용

class JSON_hyeonhang_Serializer(serializers.ModelSerializer):
    class Meta:
        model = JSON_hyeonhang        # JSON_hyeonhang 모델 사용
        fields = '__all__'            # 모든 필드 사용

class JSON_hangjeong_Serializer(serializers.ModelSerializer):
    class Meta:
        model = JSON_hangjeong        # JSON_hangjeong 모델 사용
        fields = '__all__'            # 모든 필드 사용
