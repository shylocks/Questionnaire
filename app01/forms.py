#!/usr/bin/env python
# -*- coding:utf-8 -*-
# date:"2017-12-05,19:38"

from django.forms import Form, fields, ModelForm
from django.forms import widgets as wid
from . import models


class QuestionnaireForm(Form):
    title = fields.CharField(required=True, error_messages={
        "required": "标题不能为空"
    },
                             widget=wid.TextInput(attrs={"class": "form-control"}))


class DoctorForm(ModelForm):
    class Meta:
        model = models.Doctor
        fields = "__all__"
        widgets = {
            "name": wid.TextInput(attrs={"class": "form-control", 'type': "text", "required": "true"}),
            "pwd": wid.TextInput(attrs={"class": "form-control", "type": "text", "required": "true"}),
            "hospital": wid.Select(attrs={"class": "form-control", "required": "true"}),
            "position": wid.TextInput(attrs={"class": "form-control", "required": "false"}),
        }


class HospitalForm(Form):
    name = fields.CharField(required=True, error_messages={
        "required": "医院名称不能为空"
    },
                            widget=wid.TextInput(attrs={"class": "form-control"}))
    description = fields.CharField(required=False,
                                   widget=wid.TextInput(attrs={"class": "form-control"}))


class PatientModelForm(ModelForm):
    class Meta:
        model = models.Patient
        fields = "__all__"
        error_messages = {
            "id": {"required": "系统错误"},
            "name": {"required": "姓名不能为空"},
            "gender": {"required": "性别不能为空"},
            "age": {"required": "年龄不能为空"},
            "idcard": {"required": "身份证号不能为空"},
            "nation": {"required": "名族不能为空"},
            "native_place": {"required": "籍贯不能为空"},
            "education": {"required": "教育经历不能为空"},
            "marriage": {"required": "婚姻经历不能为空"},
            "children": {"required": "子女数不能为空"}
        }
        widgets = {
            "id": wid.TextInput(attrs={"class": "form-control", 'type': "number", "required": "false", "hidden": "true"}),
            "name": wid.TextInput(attrs={"class": "form-control", 'type': "text", "required": "true"}),
            "gender": wid.Select(attrs={"class": "form-control", "required": "true"}),
            "age": wid.TextInput(attrs={"class": "form-control", "type": "number", "required": "true"}),
            "idcard": wid.TextInput(attrs={"class": "form-control", "required": "true"}),
            "nation": wid.Select(attrs={"class": "form-control", "required": "true"}),
            "native_place": wid.TextInput(attrs={"class": "form-control", "type": "text","required": "true"}),
            "education": wid.Select(attrs={"class": "form-control", "required": "true"}),
            "marriage": wid.Select(attrs={"class": "form-control", "required": "true"}),
            "children": wid.Select(attrs={"class": "form-control", "required": "true"}),
            "longest_job": wid.TextInput(attrs={"class": "form-control", "required": "false"}),
            "family_medical_history": wid.TextInput(attrs={"class": "form-control", "required": "false"})

        }


class QuestionModelForm(ModelForm):
    class Meta:
        model = models.Question
        fields = "__all__"
        error_messages = {
            "caption": {"required": "名称不能为空"},
        }
        widgets = {
            "caption": wid.TextInput(attrs={"class": "form-control", "required": "true"}),
            "ct": wid.Select(attrs={"class": "form-control", "required": "true"}),
            "part_id": wid.TextInput(attrs={"class": "form-control", "required": "true"})
        }


class OptionModelForm(ModelForm):
    class Meta:
        model = models.Option
        fields = "__all__"
        widgets = {
            "name": wid.TextInput(attrs={"class": "form-control"}),
            "score": wid.TextInput(attrs={"class": "form-control"})
        }
