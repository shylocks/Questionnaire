
from django.conf.urls import url
from django.contrib import admin
from app01 import views

urlpatterns = [
     url(r'^admin/', admin.site.urls),
     url(r'^$', views.index),
     url(r'^index/', views.index),
     url(r'^welcome/', views.index),

     url(r'^ques/', views.questionnaires),
     url(r'^edit_questionnaire/(\d+)/$', views.edit_questionnaire),
     url(r'^questionnaire/(\d+)/$', views.view_questionnaire),
     url(r'^status/(\d+)/$', views.status),
     url(r'^doctor/', views.doctor),

     url(r'^hospital/',views.hospital),

     url(r'^patient/', views.patient),
     url(r'^login/$', views.login),

     url(r'^test/',views.test),
     url(r'^question/',views.question)
]
