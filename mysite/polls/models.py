from django.db import models
from jsonfield import JSONField
# Rest API에 적용될 컬럼명들과, 이에 대응되는 컬럼 타입 지정

# Create your models here.
class JSON_jeonmoon(models.Model):
    title = models.JSONField()
    subjects = models.JSONField()
    description = models.JSONField()
    publisher = models.JSONField()
    contributors = models.JSONField()
    date = models.JSONField()
    language = models.JSONField()
    identifier = models.JSONField()


class JSON_hyeonhang(models.Model):
    type = models.JSONField()
    title = models.JSONField()
    subjects = models.JSONField()
    publisher = models.JSONField()
    date = models.JSONField()
    language = models.JSONField()
    identifier = models.JSONField()
    relation = models.JSONField()

class JSON_hangjeong(models.Model):
    type = models.JSONField()
    title = models.JSONField()
    publisher = models.JSONField()
    date = models.JSONField()
    identifier = models.JSONField()
    relation = models.JSONField()