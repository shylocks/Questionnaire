#!/usr/bin/env python
# -*- coding:utf-8 -*-
# date:"2017-12-05,19:38"

from django.forms import Form, fields,ModelForm
from django.forms import widgets as wid
from . import models


class QuestionnaireForm(Form):
    title = fields.CharField(required=True, error_messages={
        "required": "标题不能为空"
    },
                             widget=wid.TextInput(attrs={"class": "form-control"}))


class DoctorForm(Form):
    name = fields.CharField(required=True, error_messages={
        "required": "姓名不能为空"
    },
                             widget=wid.TextInput(attrs={"class": "form-control"}))
    hospital = fields.ChoiceField(required=True, error_messages={
        "required": "医院不能为空"
    },
                             choices=models.Hospital.objects.values_list("id", "name"),
                             widget=wid.Select(attrs={"class": "form-control"}))
    position = fields.CharField(required=False,
                                   widget=wid.TextInput(attrs={"class": "form-control"}))


class HospitalForm(Form):
    name = fields.CharField(required=True, error_messages={
        "required": "医院名称不能为空"
    },
                             widget=wid.TextInput(attrs={"class": "form-control"}))
    description = fields.CharField(required=False,
                            widget=wid.TextInput(attrs={"class": "form-control"}))


class PatientForm(Form):
    name = fields.CharField(required=True, error_messages={
        "required": "姓名不能为空"
    },
                             widget=wid.TextInput(attrs={"class": "form-control"}))

    age = fields.CharField(required=True, error_messages={
        "required": "姓名不能为空"
    },
                            widget=wid.TextInput(attrs={"class": "form-control"}))
    idcard = fields.CharField(required=True, error_messages={
        "required": "身份证不能为空"
    },
                            widget=wid.TextInput(attrs={"class": "form-control"}))
    nation = fields.CharField(required=True, error_messages={
        "required": "名族不能为空"
    },
                            widget=wid.TextInput(attrs={"class": "form-control"}))
    native_place = fields.CharField(required=True, error_messages={
        "required": "籍贯不能为空"
    },
                            widget=wid.TextInput(attrs={"class": "form-control"}))
    education = fields.CharField(required=True, error_messages={
        "required": "学历不能为空"
    },
                            widget=wid.Select(attrs={"class": "form-control"}))

    marriage = fields.CharField(required=True, error_messages={
        "required": "婚姻状况不能为空"
    },
                                 widget=wid.TextInput(attrs={"class": "form-control"}))

    children = fields.CharField(required=True,widget=wid.Select(attrs={"class": "form-control"}))

    longest_job = fields.CharField(required=False, widget=wid.TextInput(attrs={"class": "form-control"}))
    family_medical_history = fields.CharField(required=False, widget=wid.TextInput(attrs={"class": "form-control"}))


class QuestionModelForm(ModelForm):
    class Meta:
        model = models.Question
        fields = "__all__"
        error_messages = {
            "caption": {"required": "名称不能为空"},

        }
        widgets = {
            "caption": wid.Textarea(attrs={"class":"form-control", "rows": "2" ,"cols": "60"}),
            "ct": wid.Select(attrs={"class":"form-control"}),
            "part_id": wid.Textarea( attrs={"class":"form-control", "rows": "1" ,"cols": "20"})
        }


class OptionModelForm(ModelForm):
    class Meta:
        model = models.Option
        fields = "__all__"
        widgets = {
            "name": wid.TextInput(attrs={"class": "form-control"}),
            "score": wid.TextInput(attrs={"class": "form-control"})

        }