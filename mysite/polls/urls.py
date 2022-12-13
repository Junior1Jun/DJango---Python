from django.urls import path

from . import views

urlpatterns = [
    # ex /polls/


    path('json/',views.JSON, name = 'JSON'),

    path('json/db/',views.saveDB, name = 'saveDB'),

    # path('jsonjson/',views.JSON2,name = 'JSON2'),

    # '<int:question_id>/vote/'는 쟝고에서 지원하는 url패턴
]