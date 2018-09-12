
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
    url(r'^edit_questionnaire/(\d+)/$', views.edit_questionnaire),

    url(r'^doctor/', views.doctor),
    url(r'^add_doctor/$', views.add_doctor),
    url(r'^edit_doctor/(\d+)/$', views.edit_doctor),

    url(r'^patient/', views.patient),
    url(r'^add_patient/',views.add_patient),
    url(r'^login/$', views.login),
    url(r'^(student/evaluate/\d+)/(\d+)/$', views.score),

]
