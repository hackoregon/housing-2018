from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [
    url(r'^slides/permits/(?P<date_filter>\d+)', views.permits),
    url(r'^slides/permits/', views.permits),

]
urlpatterns = format_suffix_patterns(urlpatterns)