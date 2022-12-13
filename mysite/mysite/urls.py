"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static
from polls.views import JSONListAPI
from django.conf import settings

urlpatterns = [
    path('polls/',include('polls.urls')), # polls.urls에서 polls은 앱을 의미함.
    path('admin/', admin.site.urls),
    path('api/questions/<int:page_num>/<int:content_num>',JSONListAPI.as_view())
]

# django.urls의 include를 사용해 url들을 계층적으로 관리함.
# path('path/', myapp.views.home, name='hello_world') 는 http://127.0.0.1:8000/polls/json/로 접속했을 때,
# myapp.views.home를 실행하라는 뜻임.

# path('products/', include('product.urls')) 는 http://127.0.0.1:8000/products/ 로 시작하는 
# 모든 URL 들은 product 앱 안의 urls.py 파일 안에서 관리할 것이다.
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)