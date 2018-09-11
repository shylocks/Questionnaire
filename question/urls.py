
from django.conf.urls import url
from django.contrib import admin
from app01 import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.index),
    url(r'^index/', views.index),
    url(r'^welcome/', views.index),
    url(r'^ques/', views.questionnaires),
    url(r'^add_questionnaire/$', views.add_questionnaire),
    url(r'^delete_questionnaire/(\d+)/$', views.delete_questionnaire),
    url(r'^edit_questionnaire/(\d+)/$', views.edit_questionnaire),
    url(r'^member/', views.member),
    url(r'^add_member/$', views.add_member),
    url(r'^delete_member/(\d+)/$', views.delete_member),
    url(r'^edit_member/(\d+)/$', views.edit_member),
    url(r'^login/$', views.login),
    url(r'^(student/evaluate/\d+)/(\d+)/$', views.score),

]
