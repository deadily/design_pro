from django.urls import re_path
from . import views

urlpatterns = [
    re_path(r'^$', views.index, name='index'),
    re_path(r'^login/$', views.user_login, name='login'),
    re_path(r'^register/$', views.register, name='register'),
    re_path(r'^logout/$', views.user_logout, name='logout'),
    re_path(r'^user/requests/$', views.user_requests, name='user_requests'),
    re_path(r'^user/request/create/$', views.create_request, name='create_request'),
    re_path(r'^user/request/delete/(?P<req_id>\d+)/$', views.delete_request, name='delete_request'),
]