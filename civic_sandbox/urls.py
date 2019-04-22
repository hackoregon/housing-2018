from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from . import views
from . import packages_view


urlpatterns = [
    url(r'^slides/permits/(?P<date_filter>\d+)', views.permits),
    url(r'^slides/permits/', views.permits),
    url(r'^package_info/', packages_view.packages_view, name='package_info'),

]
urlpatterns = format_suffix_patterns(urlpatterns)