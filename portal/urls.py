from django.urls import path, re_path
from . import views

urlpatterns = [
    re_path(r'^$', views.index, name='index'),
    re_path(r'^login/$', views.user_login, name='login'),
    re_path(r'^register/$', views.register, name='register'),
    re_path(r'^logout/$', views.user_logout, name='logout'),
    re_path(r'^user/requests/$', views.user_requests, name='user_requests'),
    re_path(r'^user/request/create/$', views.create_request, name='create_request'),
    re_path(r'^user/request/delete/(?P<req_id>\d+)/$', views.delete_request, name='delete_request'),

    re_path(r'^superadmin/$', views.admin_dashboard, name='admin_dashboard'),
    re_path(r'^superadmin/status/(?P<req_id>\d+)/$', views.change_status, name='change_status'),
    re_path(r'^superadmin/category/add/$', views.add_category, name='add_category'),
    re_path(r'^superadmin/category/delete/(?P<cat_id>\d+)/$', views.delete_category, name='delete_category'),
]