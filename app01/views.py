# -*- coding: utf-8 -*-
import json

from django.shortcuts import render, HttpResponse, redirect
from django.core.exceptions import ValidationError
from django.forms import Form
from django.db.models import Count
from django.forms import fields
from django.forms import widgets
from urllib.parse import parse_qs
from . import models
from .forms import QuestionnaireForm, QuestionModelForm, OptionModelForm, DoctorForm, PatientModelForm, HospitalForm
import random
import pandas as pd
pd.options.display.max_colwidth = 100
import re
from wordcloud import WordCloud
import jieba
# Create your views here.


def index(request):
    return render(request, 'index.html', )


def status(request, questionnaire_id):
    question_list = models.Question.objects.filter(questionnaire_id=questionnaire_id).order_by('part_id')

    def inner():
        for que in question_list:
            temp = {"obj": que, "options_cls": "hide", "options": None}
            if not que.ct == 3:
                temp["options_cls"] = ""

                def inner_lop(xxx):
                    answer_list = models.Answer.objects.filter(question_id=xxx)
                    df = pd.DataFrame(
                        {'OptionID': [w.option_id for w in answer_list],
                         'PatientID': [w.patient_id for w in answer_list]})
                    answerDF = df.groupby('OptionID').agg({'PatientID': 'count'}).reset_index().sort_values(
                        by='OptionID')
                    OptionIDList = answerDF['OptionID'].values.tolist()
                    PatientIDList = answerDF['PatientID'].values.tolist()
                    temp = len(answer_list)
                    for i in range(0, len(OptionIDList)):
                        yield {"Option": models.Option.objects.filter(id=OptionIDList[i]).first().name,
                               "Count": PatientIDList[i], "Proportion": '%.2f' % (PatientIDList[i]/temp * 100)}
                temp["options"] = inner_lop(que.id)
            yield temp
    return render(request, 'status.html', {"form_list": inner()})


def fake_data(questionnaire_id, patient_id, doctor_id):
    import time
    import datetime
    time_stamp = time.mktime(datetime.datetime.now().timetuple())
    models.Res.objects.create(time_stamp=time_stamp,patient_id=patient_id, doctor_id=doctor_id)
    res_id = models.Res.objects.filter(time_stamp=time_stamp).first().id
    question_list = models.Question.objects.filter(questionnaire_id=questionnaire_id)
    for question in question_list:
        option_list = models.Option.objects.filter(question_id=question.id)
        option_id_list = [w.id for w in option_list]
        models.Answer.objects.create(option_id=option_id_list[random.randint(0, len(option_id_list)-1)], question_id=question.id, patient_id=patient_id, res_id=res_id)


def questionnaires(request):
    if request.method == "GET":
        pars = parse_qs(request.GET.urlencode())
        if pars.get('method'):
            if pars['method'][0] == 'delete':
                models.Questionnaire.objects.filter(id=pars['id'][0]).delete()
            if pars['method'][0] == 'add':
                return render(request, 'models/QuestionnaireModel.html', )
            if pars['method'][0] == 'view_static':
                ques = models.Questionnaire.objects.filter(id=pars['id'][0]).first()
                question_list = models.Question.objects.filter(questionnaire_id=ques.id)
                answer_list = models.Answer.objects.all()
                question_id_list=[]
                for question in question_list:
                    question_id_list.append(question.id)
                participant_id_list = []
                for answer in answer_list:
                    if answer.patient_id not in participant_id_list:
                        participant_id_list.append(answer.patient_id)
                score_list = []
                for participant_id in participant_id_list:
                    this_score = 0
                    this_answer_list = models.Answer.objects.filter(patient_id=participant_id)
                    for answer in this_answer_list:
                        if answer.question_id in question_id_list:
                            tmp = models.Question.objects.filter(id=answer.question_id).first()
                            if tmp.ct == 2:
                                this_score += models.Option.objects.filter(id=answer.option_id).first().score
                    score_list.append(this_score)

                class ipart:
                    name = ""
                    score = 0

                participant_list = []
                for i in range(0,len(participant_id_list)):
                    tmp = ipart()
                    tmp.name = models.Patient.objects.filter(id=participant_id_list[i]).first().name
                    tmp.score = score_list[i]
                    participant_list.append(tmp)

                return render(request, 'status.html', locals())
    elif request.is_ajax():
        data = json.loads(request.body.decode("utf-8"))
        models.Questionnaire.objects.create(title=data.get("title"))
    questionnaire_list = models.Questionnaire.objects.all()
    return render(request, 'ques.html', locals())


def doctor(request):
    if request.method == "GET":
        pars = parse_qs(request.GET.urlencode())
        if pars.get('method'):
            if pars['method'][0] == 'delete':
                models.Doctor.objects.filter(id=pars['id'][0]).delete()
            if pars['method'][0] == 'reset':
                models.Doctor.objects.filter(id=pars['id'][0]).update(pwd="123456")
            if pars['method'][0] == 'add':

                form = DoctorForm()
                return render(request, 'models/DoctorModel.html', {"form": form})
    else:
        form = DoctorForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data.get("name")
            id = 10001 + len(models.Doctor.objects.all())
            hospital = form.cleaned_data.get("hospital")
            position = form.cleaned_data.get("position")
            models.Doctor.objects.create(id=id, name=name, pwd="123456", hospital_id=hospital,position=position)
            return redirect("/doctor/")
    Doctor_list = models.Doctor.objects.all()
    return render(request, 'doctor.html', locals())


def hospital(request):
    if request.method == "GET":
        pars = parse_qs(request.GET.urlencode())
        if pars.get('method'):
            if pars['method'][0] == 'delete':
                models.Hospital.objects.filter(id=pars['id'][0]).delete()
            if pars['method'][0] == 'add':
                form = HospitalForm()
                return render(request, 'models/HospitalModel.html', {"form": form})
    else:
        form = HospitalForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data.get("name")
            description = form.cleaned_data.get("description")
            id = 1 + len(models.Hospital.objects.all())
            models.Hospital.objects.create(id=id, name=name, description=description)
            return redirect("/hospital/")
    Hospital_list = models.Hospital.objects.all()
    return render(request, 'hospital.html', locals())


def patient(request):
    if request.method == "GET":
        pars = parse_qs(request.GET.urlencode())
        if pars.get('method'):
            if pars['method'][0] == 'delete':
                models.Patient.objects.filter(id=pars['id'][0]).delete()
            elif pars['method'][0] == 'further':
                '''
                questionnaire_list = models.Questionnaire.objects.all()
                questionnaire_name_list=[]
                score_list = []
                for ques in questionnaire_list:
                    questionnaire_name_list.append(ques.title)
                    question_list = models.Question.objects.filter(questionnaire_id=ques.id)
                    answer_list = models.Answer.objects.all()
                    question_id_list = []
                    for question in question_list:
                        question_id_list.append(question.id)
                    this_score = 0
                    this_answer_list = models.Answer.objects.filter(patient_id=pars['id'][0])
                    for answer in this_answer_list:
                        if answer.question_id in question_id_list:
                            tmp = models.Question.objects.filter(id=answer.question_id).first()
                            if tmp.ct == 2:
                                this_score += models.Option.objects.filter(id=answer.option_id).first().score
                    score_list.append(this_score)

                class ipart:
                    name = ""
                    score = 0

                participant_list = []
                for i in range(0, len(questionnaire_name_list)):
                    tmp = ipart()
                    tmp.name = questionnaire_name_list[i]
                    tmp.score = score_list[i]
                    participant_list.append(tmp)'''
                form = PatientModelForm(instance=models.Patient.objects.filter(id=pars['id'][0]).first())
                idd = pars['id'][0]
                return render(request, 'models/PatientModel.html', locals())
            elif pars['method'][0] == 'add':
                form = PatientModelForm()
                #print(form)
                return render(request, 'models/PatientModel.html',locals())
    elif request.method == "POST":
        form = PatientModelForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data.get("name")
            gender = form.cleaned_data.get("gender")
            age = form.cleaned_data.get("age")
            idcard = form.cleaned_data.get("idcard")
            nation = form.cleaned_data.get("nation")
            native_place = request.POST.get("native_place")
            education = form.cleaned_data.get("education")
            marriage = form.cleaned_data.get("marriage")
            children = form.cleaned_data.get("children")
            longest_job = form.cleaned_data.get("longest_job", "无")
            family_medical_history = form.cleaned_data.get("family_medical_history", "无")
            if request.POST.get("idd"):
                models.Patient.objects.filter(id=request.POST.get("idd")).update(name=name, gender=gender, age=age, idcard=idcard,
                                              nation=nation, native_place=native_place,
                                              education=education, marriage=marriage,
                                              children=children, longest_job=longest_job,
                                              family_medical_history=family_medical_history)
            else:
                models.Patient.objects.create(name=name, gender=gender, age=age, idcard=idcard,
                                          nation=nation, native_place=native_place,
                                          education=education, marriage=marriage,
                                          children=children, longest_job=longest_job,
                                          family_medical_history=family_medical_history)
        else:
            print(form.errors)


    Patient_list = models.Patient.objects.all()
    return render(request, 'patient.html', locals())


def login(request):
    if request.method == "GET":
        return render(request, 'login.html')
    elif request.is_ajax():

        state = {"state": None}
        username = request.POST.get("user")

        if username == "":
            state["state"] = "user_none"
            return HttpResponse(json.dumps(state))
        password = request.POST.get("pwd")

        if password == "":
            state["state"] = "pwd_none"
            return HttpResponse(json.dumps(state))

        user = models.Admin.objects.filter(name=username, pwd=password).first()

        if user:
            state["state"] = "login_success"
            request.session["username"] = user.name
            request.session["id"] = user.id
            request.session["admin"] = "1"
        else:
            state["state"] = "failed"

        return HttpResponse(json.dumps(state))


def view_questionnaire(request, pid):
    if request.method == "GET":
        pars = parse_qs(request.GET.urlencode())
        if pars.get("method"):
            if pars['method'][0] == 'delete':
                questionID = pars['QuestionID'][0]
                models.Question.objects.filter(id=questionID).delete()
            if pars['method'][0] == 'viewPart':
                partID = pars['PartID'][0]
                part = models.Part.objects.filter(id=partID, questionnaire_id=pid).first()
                return render(request, 'models/PartModel.html', locals())
    elif request.is_ajax():
        item = json.loads(request.body.decode("utf-8"))
        models.Part.objects.filter(part_id=item.get("id"), questionnaire_id=pid).update(description=item.get("description"))
    Questionnaire = models.Questionnaire.objects.filter(id=pid).first()
    question_list = models.Question.objects.filter(questionnaire_id=pid)
    parts = []
    option_list = models.Option.objects.all()
    for ques in question_list:
        if ques.part_id not in parts:
            parts.append(ques.part_id)
    partTemp = models.Part.objects.filter(questionnaire_id=pid)
    for part in partTemp: #防止出现新问卷没有问题的情况
        if part.part_id not in parts:
            parts.append(part.part_id)
    parts.sort()
    qid = int(pid)
    questionnaire_id = pid
    if not len(parts):
        models.Part.objects.create(questionnaire_id=questionnaire_id, part_id=1)
        parts.append(1)
    for part in parts:
        if not models.Part.objects.filter(questionnaire_id=questionnaire_id,part_id=part).first():
            models.Part.objects.create(questionnaire_id=questionnaire_id,part_id=part)
    part_list = models.Part.objects.all()
    return render(request, 'questionnaire.html', locals())


def edit_questionnaire(request, pid):
    '''
      编辑问卷
      :param request:
      :param pid: 问卷id
      :return:
      '''
    if request.method == "GET":
        def inner():
            que_list = models.Question.objects.filter(questionnaire_id=pid)  # 获取当前问卷的所有问题
            if not que_list:  # 如果没有，表示该问卷还没有问题
                form = QuestionModelForm()
                yield {'form': form, 'obj': None, 'options_cls': 'hide', 'options': None}
            else:
                for que in que_list:
                    form = QuestionModelForm(instance=que)
                    temp = {"form": form, "obj": que, "options_cls": "hide", "options": None}
                    if que.ct == 2:
                        temp["options_cls"] = ""

                        # 获取当前问题的所有选项
                        def inner_lop(xxx):
                            option_list = models.Option.objects.filter(question=xxx)
                            for v in option_list:
                                yield {"form": OptionModelForm(instance=v), "obj": v}

                        temp["options"] = inner_lop(que)
                    yield temp

        return render(request, "edit_questionnaire.html", {"form_list": inner()})

    else:
        data = json.loads(request.body.decode("utf-8"))  # 获取当前问卷的所有问题

        question_list = models.Question.objects.filter(questionnaire_id=pid)  # 获取用户提交所有问题的id
        post_id_list = [i.get("id") for i in data]  # 获取数据库中已有问题的ID
        question_id_list = [str(i.id) for i in question_list]  # 获取数据库中已有问题的ID
        del_id_list = set(question_id_list).difference(post_id_list)  # 利用集合去重获取需要删除的ID
        for del_id in del_id_list:
            models.Question.objects.filter(id=del_id).delete()
        for item in data:
            qid = item.get("id")
            caption = item.get("caption")
            ct = item.get("ct")
            options = item.get("options")
            part_id = item.get("part_id")
            # 如果用户传过来的id不在数据库原有id列表中的时候，表示要新增
            if qid not in question_id_list:
                new_question_obj = models.Question.objects.create(caption=caption, ct=ct, questionnaire_id=pid, part_id=part_id)
                if ct == 2:
                    for op in options:
                        models.Option.objects.create(question=new_question_obj, name=op.get("name"),
                                                     score=op.get("score"))
            # 否则表示要更新
            else:
                models.Question.objects.filter(id=qid).update(caption=caption, ct=ct, questionnaire_id=pid, part_id=part_id)
                if not options:  # 如果没有选项表示要删除选项
                    models.Option.objects.filter(question_id=qid).delete()
                else:
                    for op in options:
                        models.Option.objects.filter(question_id=qid).update(name=op.get("name"), score=op.get("score"), question_id=qid)
        return HttpResponse("ok")


def test(request):
    return render(request, "test.html", )


def question(request):
    if request.method == "GET":
        pars = parse_qs(request.GET.urlencode())
        if pars['method'][0] == 'add':
            questionnaireID = pars['QuestionnaireID'][0]
            form = QuestionModelForm()
            item = {'form': form, 'obj': None, 'options_cls': 'hide', 'options': None}
            return render(request, "models/QuestionModel.html", locals())
        if pars['method'][0] == 'view':
            questionID = pars['QuestionID'][0]
            que = models.Question.objects.filter(id=questionID).first()
            form = QuestionModelForm(instance=que)
            item = {"form": form, "obj": que, "options": None}
            if que.ct == 2 or que.ct == 1:
                item["options_cls"] = ""
                # 获取当前问题的所有选项

                def inner_lop(xxx):
                    option_list = models.Option.objects.filter(question=xxx)
                    for v in option_list:
                        yield {"form": OptionModelForm(instance=v), "obj": v}
                item["options"] = inner_lop(que)
            print(item)
            return render(request, "models/QuestionModel.html", locals())
    elif request.is_ajax():
        item = json.loads(request.body.decode("utf-8"))
        print(item)
        qid = item.get("id")
        caption = item.get("caption")
        ct = item.get("ct")
        options = item.get("options")
        part_id = item.get("part_id")
        pid = item.get("questionnaire_id")
        if qid == "":
            models.Question.objects.create(caption=caption, ct=ct, part_id=part_id, questionnaire_id=pid)
            qid = models.Question.objects.last().id
        else:
            models.Question.objects.filter(id=qid).update(caption=caption, ct=ct, part_id=part_id)
            models.Option.objects.filter(question_id=qid).delete()
        for op in options:
            models.Option.objects.create(name=op.get("name"), score=op.get("score"), question_id=qid)

        return HttpResponse("ok")
    return render(request, "models/QuestionModel.html", )
