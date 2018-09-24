# -*- coding: utf-8 -*-
import json

from django.shortcuts import render, HttpResponse, redirect

from urllib.parse import parse_qs
from . import models
from .forms import QuestionModelForm, OptionModelForm, DoctorForm, PatientModelForm, HospitalForm
import random
import pandas as pd
import numpy as np
import math

pd.options.display.max_colwidth = 100
import re
from wordcloud import WordCloud
import jieba
# Create your views here.
import os

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))


def index(request):
    '''doctor_sum = models.Doctor.objects.all().count()
    patient_sum = models.Patient.objects.all().count()
    for i in range(patient_sum):
        print(i+1)
        fake_res_data(1, i+1, 10000+random.randint(1, doctor_sum-10))'''
    if request.session['admin'] == '0':
        user = models.Doctor.objects.filter(id=request.session['id']).first()
        patient_num = len(list(set(list(
            models.Res.objects.filter(doctor_id=request.session['id']).values_list("patient_id", flat=True)))))
        res_num = models.Res.objects.filter(doctor_id=request.session['id']).count()
        return render(request, 'doctor/index.html', locals())
    user = request.session["username"]
    return render(request, 'index.html', locals())


def status(request):
    questionnaire_list = models.Questionnaire.objects.all()
    res_list = models.Res.objects.all()
    for res in res_list:
        if not res.questionnaire_id:
            if models.Answer.objects.filter(res_id=res.id).first() is None:
                models.Res.objects.filter(id=res.id).delete()
            else:
                temp_question_id = models.Answer.objects.filter(res_id=res.id).first().question_id
                temp_questionnaire_id = models.Question.objects.filter(id=temp_question_id).first().questionnaire_id
                models.Res.objects.filter(id=res.id).update(questionnaire_id=temp_questionnaire_id)
        if not res.score:
            print(res.id)
            this_score = 0
            this_answer_list = models.Answer.objects.filter(res_id=res.id)
            for answer in this_answer_list:
                tmp = models.Question.objects.filter(id=answer.question_id).first()
                if not tmp.ct == 3:
                    this_score += models.Option.objects.filter(id=answer.option_id).first().score
            models.Res.objects.filter(id=res.id).update(score=this_score)

    def inner():
        for questionnaire in questionnaire_list:
            df = pd.DataFrame({'score': list(
                models.Res.objects.filter(questionnaire_id=questionnaire.id).values_list('score', flat=True))})
            temp = {"obj": questionnaire,
                    "status": {"mean": '%.2f' % float(df.mean()), "max": float(df.max()), "min": float(df.min()),
                               "sum": int(df.count())}}
            yield temp

    return render(request, 'status.html', {"form_list": inner()})


def get_page_list(now_page, total_page):
    previous_page = 0
    next_page = 0
    if total_page < 12:
        page_list = np.arange(1, total_page + 1)
        return {'previous_page': previous_page, 'page_list': page_list, 'next_page': next_page}
    if total_page - now_page < 12:
        page_list = np.arange(total_page - 11, total_page + 1)
        previous_page = total_page - 12
    else:
        if now_page < 13:
            page_list = np.arange(1, 13)
            next_page = 13
        elif not (now_page - 1) % 12:
            page_list = np.arange(now_page, now_page + 12)
            previous_page = int(now_page / 12) * 12
            next_page = int(now_page / 12 + 1) * 12 + 1
        elif not now_page % 12:
            page_list = np.arange(now_page - 11, now_page + 1)
            previous_page = int(now_page / 12 - 1) * 12
            next_page = now_page + 1
        else:
            page_list = np.arange(int(now_page / 12) * 12 + 1, int(now_page / 12) * 12 + 13)
            previous_page = int(now_page / 12) * 12
            next_page = int(now_page / 12 + 1) * 12 + 1
    return {'previous_page': previous_page, 'page_list': page_list, 'next_page': next_page}


def summary(request, questionnaire_id):
    res_list_all = models.Res.objects.filter(questionnaire_id=questionnaire_id)
    total_page = math.ceil(res_list_all.count() / 10)
    now_page = 1
    if request.method == "GET":
        pars = parse_qs(request.GET.urlencode())
        if pars.get('method'):
            if pars['method'][0] == 'view':
                if pars.get('page'):
                    now_page = int(pars['page'][0])
    page = get_page_list(now_page, total_page)
    qid = questionnaire_id
    res_list = res_list_all[(now_page - 1) * 10:now_page * 10]
    return render(request, 'summary.html', locals())


def analysis(request, questionnaire_id):
    title = models.Questionnaire.objects.filter(id=questionnaire_id).first().title
    question_list = models.Question.objects.filter(questionnaire_id=questionnaire_id).order_by('part_id')

    def inner():
        for que in question_list:
            temp = {"obj": que, "options_cls": "hide", "options": None, "title": "选项"}
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
                               "Count": PatientIDList[i], "Proportion": '%.2f' % (PatientIDList[i] / temp * 100)}

                temp["options"] = inner_lop(que.id)
            yield temp

    return render(request, 'analysis.html', {"form_list": inner(), "title": title})


def fake_name():
    first_name = [
        '赵', '钱', '孙', '李', '周', '吴', '郑', '王', '冯', '陈', '褚', '卫', '蒋', '沈', '韩', '杨', '朱', '秦', '尤', '许',
        '何', '吕', '施', '张', '孔', '曹', '严', '华', '金', '魏', '陶', '姜', '戚', '谢', '邹', '喻', '柏', '水', '窦', '章',
        '云', '苏', '潘', '葛', '奚', '范', '彭', '郎', '鲁', '韦', '昌', '马', '苗', '凤', '花', '方', '俞', '任', '袁', '柳',
        '酆', '鲍', '史', '唐', '费', '廉', '岑', '薛', '雷', '贺', '倪', '汤', '滕', '殷', '罗', '毕', '郝', '邬', '安', '常',
        '乐', '于', '时', '傅', '皮', '卞', '齐', '康', '伍', '余', '元', '卜', '顾', '孟', '平', '黄', '和', '穆', '萧', '尹',
        '姚', '邵', '堪', '汪', '祁', '毛', '禹', '狄', '米', '贝', '明', '臧', '计', '伏', '成', '戴', '谈', '宋', '茅', '庞',
        '熊', '纪', '舒', '屈', '项', '祝', '董', '梁']

    def last_name():
        head = random.randint(0xb0, 0xf7)
        body = random.randint(0xa1, 0xfe)
        val = f'{head:x}{body:x}'
        str = bytes.fromhex(val).decode('gb2312')
        return str

    return random.choice(first_name) + last_name() + last_name()


def fake_patient_data(num):
    cites_df = pd.read_csv(os.path.join(PROJECT_ROOT, 'cities.csv'))
    province_df = pd.read_csv(os.path.join(PROJECT_ROOT, 'provinces.csv'))
    for i in range(num):
        print(i)
        ra = random.randint(0, len(cites_df) - 1)
        native_place = province_df[province_df['code'] == cites_df.iloc[ra, 2]].iloc[0, 1] + cites_df.iloc[ra, 1]
        name = fake_name()
        gender = random.randint(1, 2)
        age = random.randint(18, 90)
        idcard = str(random.randint(100000, 999999)) + str(random.randint(1900, 2018)) + str(
            random.randint(10, 12)) + str(random.randint(10, 31)) + str(random.randint(1000, 9999))
        nation = str(random.randint(1, 56))
        education = str(random.randint(1, 6))
        marriage = str(random.randint(1, 5))
        children = str(random.randint(0, 7))
        models.Patient.objects.create(name=name, gender=gender, age=age, idcard=idcard, nation=nation,
                                      native_place=native_place, education=education, marriage=marriage,
                                      children=children)


def fake_doctor_data(num):
    hospital_sum = int(models.Hospital.objects.all().count())
    for i in range(num):
        print(i)
        id = 10001 + len(models.Doctor.objects.all())
        models.Doctor.objects.create(id=id, hospital_id=random.randint(1, hospital_sum - 1), name=fake_name())


def fake_res_data(questionnaire_id, patient_id, doctor_id):
    import time
    import datetime
    time_stamp = time.mktime(datetime.datetime.now().timetuple())
    models.Res.objects.create(time_stamp=time_stamp, patient_id=patient_id, doctor_id=doctor_id,
                              questionnaire_id=questionnaire_id)
    res_id = models.Res.objects.all().last().id
    question_list = models.Question.objects.filter(questionnaire_id=questionnaire_id)
    for question in question_list:
        option_list = models.Option.objects.filter(question_id=question.id)
        option_id_list = [w.id for w in option_list]
        models.Answer.objects.create(option_id=option_id_list[random.randint(0, len(option_id_list) - 1)],
                                     question_id=question.id, patient_id=patient_id, res_id=res_id)


def questionnaires(request):
    questionnaire_list = models.Questionnaire.objects.all()
    for ques in questionnaire_list:
        models.Questionnaire.objects.filter(id=ques.id).update(
            finished_num=models.Res.objects.filter(questionnaire_id=ques.id).count())
    res_list = models.Res.objects.all()
    if request.method == "GET":
        pars = parse_qs(request.GET.urlencode())
        if pars.get('method'):
            if pars['method'][0] == 'delete':
                models.Questionnaire.objects.filter(id=pars['id'][0]).delete()
            if pars['method'][0] == 'add':
                return render(request, 'models/QuestionnaireModel.html', )
    elif request.is_ajax():
        data = json.loads(request.body.decode("utf-8"))
        models.Questionnaire.objects.create(title=data.get("title"))
    questionnaire_list = models.Questionnaire.objects.all()
    return render(request, 'ques.html', locals())


def doctor(request):
    now_page = 1
    doctor_list_all = models.Doctor.objects.all()
    total_page = math.ceil(doctor_list_all.count() / 8)
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
            if pars['method'][0] == 'view':
                if pars.get('page'):
                    now_page = int(pars['page'][0])

    else:
        form = DoctorForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data.get("name")
            id = 10001 + len(models.Doctor.objects.all())
            hospital = form.cleaned_data.get("hospital")
            position = form.cleaned_data.get("position")
            models.Doctor.objects.create(id=id, name=name, pwd="123456", hospital_id=hospital, position=position)
            return redirect("/doctor/")
    page = get_page_list(now_page, total_page)
    doctor_list = doctor_list_all[(now_page - 1) * 8:now_page * 8]
    return render(request, 'doctor.html', locals())


def hospital(request):
    '''
    hospital_df = pd.read_csv(os.path.join(PROJECT_ROOT, 'hospital.csv'), encoding='UTF-8')
    description_list = hospital_df['小类'].values.tolist()
    for i, hospital in enumerate(hospital_df['机构名称'].values.tolist()):
        id = 1 + len(models.Hospital.objects.all())
        models.Hospital.objects.create(id=id,name=hospital,description=description_list[i])
    '''
    now_page = 1
    hospital_list_all = models.Hospital.objects.all()
    total_page = math.ceil(hospital_list_all.count() / 10)
    if request.method == "GET":
        pars = parse_qs(request.GET.urlencode())
        if pars.get('method'):
            if pars['method'][0] == 'delete':
                models.Hospital.objects.filter(id=pars['id'][0]).delete()
            if pars['method'][0] == 'add':
                form = HospitalForm()
                return render(request, 'models/HospitalModel.html', {"form": form})
            if pars['method'][0] == 'view':
                if pars.get('page'):
                    now_page = int(pars['page'][0])
    else:
        form = HospitalForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data.get("name")
            description = form.cleaned_data.get("description")
            id = 1 + len(models.Hospital.objects.all())
            models.Hospital.objects.create(id=id, name=name, description=description)
            return redirect("/hospital/")
    page = get_page_list(now_page, total_page)
    hospital_list = hospital_list_all[(now_page - 1) * 10:now_page * 10]
    return render(request, 'hospital.html', locals())


def patient(request):
    patient_list_all = models.Patient.objects.all()
    total_page = math.ceil(patient_list_all.count() / 8)
    now_page = 1
    if request.method == "GET":
        pars = parse_qs(request.GET.urlencode())
        if pars.get('method'):
            if pars['method'][0] == 'delete':
                models.Patient.objects.filter(id=pars['id'][0]).delete()
            elif pars['method'][0] == 'further':
                form = PatientModelForm(instance=models.Patient.objects.filter(id=pars['id'][0]).first())
                idd = pars['id'][0]
                return render(request, 'models/PatientModel.html', locals())
            elif pars['method'][0] == 'add':
                form = PatientModelForm()
                return render(request, 'models/PatientModel.html', locals())
            elif pars['method'][0] == 'fake':
                fake_patient_data(100)
            elif pars['method'][0] == 'view':
                now_page = int(pars['page'][0])
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
                models.Patient.objects.filter(id=request.POST.get("idd")).update(name=name, gender=gender, age=age,
                                                                                 idcard=idcard,
                                                                                 nation=nation,
                                                                                 native_place=native_place,
                                                                                 education=education, marriage=marriage,
                                                                                 children=children,
                                                                                 longest_job=longest_job,
                                                                                 family_medical_history=family_medical_history)
            else:
                models.Patient.objects.create(name=name, gender=gender, age=age, idcard=idcard,
                                              nation=nation, native_place=native_place,
                                              education=education, marriage=marriage,
                                              children=children, longest_job=longest_job,
                                              family_medical_history=family_medical_history)
        else:
            print(form.errors)
    page = get_page_list(now_page, total_page)
    patient_list = patient_list_all[(now_page - 1) * 8:now_page * 8]
    return render(request, 'patient.html', locals())


def admin(request):
    if request.method == "GET":
        return render(request, 'admin.html')
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
        models.Part.objects.filter(part_id=item.get("id"), questionnaire_id=pid).update(
            description=item.get("description"))
    Questionnaire = models.Questionnaire.objects.filter(id=pid).first()
    question_list = models.Question.objects.filter(questionnaire_id=pid)
    parts = []
    option_list = models.Option.objects.all()
    for ques in question_list:
        if ques.part_id not in parts:
            parts.append(ques.part_id)
    partTemp = models.Part.objects.filter(questionnaire_id=pid)
    for part in partTemp:  # 防止出现新问卷没有问题的情况
        if part.part_id not in parts:
            parts.append(part.part_id)
    parts.sort()
    qid = int(pid)
    questionnaire_id = pid
    if not len(parts):
        models.Part.objects.create(questionnaire_id=questionnaire_id, part_id=1)
        parts.append(1)
    for part in parts:
        if not models.Part.objects.filter(questionnaire_id=questionnaire_id, part_id=part).first():
            models.Part.objects.create(questionnaire_id=questionnaire_id, part_id=part)
    part_list = models.Part.objects.all()
    return render(request, 'questionnaire.html', locals())


def classify(request, pid):
    title = models.Questionnaire.objects.filter(id=pid).first().title
    res_list = models.Res.objects.filter(questionnaire_id=pid)
    df = pd.DataFrame({'分数': list(res_list.values_list('score', flat=True)),
                       '民族': [w.patient.nation_type[w.patient.nation - 1][1] for w in res_list],
                       '年龄': [w.patient.age for w in res_list],
                       '性别': [w.patient.gender_type[w.patient.gender - 1][1] for w in res_list],
                       '籍贯': [w.patient.native_place[:2] for w in res_list],
                       '教育程度': [w.patient.education_type[w.patient.education - 1][1] for w in res_list],
                       '婚姻状况': [w.patient.marriage_type[w.patient.marriage - 1][1] for w in res_list],
                       '子女数': [w.patient.children_type[w.patient.children - 1][1] for w in res_list],
                       'id': list(res_list.values_list('id', flat=True))
                       })  # 载入大数据模板
    '''# 分段计数
    df['分段计数'] = pd.cut(df['score'], 5)
    print(df.groupby('分段计数').agg({'score': 'count'}).reset_index().sort_values(
        by='分段计数'))
    # 分民族
    print(df.groupby('nation').agg({'score': 'count'}).reset_index().sort_values(
        by='score', ascending=False)[:10])
    # 分年龄
    df['分段计数'] = pd.cut(df['age'], 5)
    print(df.groupby('分段计数').agg({'age': 'count'}).reset_index().sort_values(
        by='分段计数'))
    # 分性别
    print(df.groupby('gender').agg({'id': 'count'}).reset_index())
    # 分籍贯
    print(df.groupby('native_place').agg({'id': 'count'}).reset_index().sort_values(
        by='id', ascending=False)[:10])
    # 分教育程度
    print(df.groupby('education').agg({'id': 'count'}).reset_index())
    # 分婚姻状况
    print(df.groupby('marriage').agg({'id': 'count'}).reset_index())
    # 分子女数
    print(df.groupby('children').agg({'id': 'count'}).reset_index())'''
    obj_list = [{'caption': '分数'}, {'caption': '民族'}, {'caption': '年龄'}, {'caption': '性别'}, {'caption': '籍贯'},
                {'caption': '教育程度'}, {'caption': '婚姻状况'}, {'caption': '子女数'}]
    length = res_list.count()

    def inner():
        for obj in obj_list:
            temp = {"obj": obj, "options": None, "title": obj['caption']}

            def inner_lop(xxx):
                if xxx == '分数':
                    df['健康程度'] = pd.cut(df[xxx], [0, 30, 90, 125, 360], labels=['健康', '轻度痴呆', '中度痴呆', '重度痴呆'])
                    answerDF = df.groupby('健康程度').agg({'id': 'count'}).reset_index()
                    OptionIDList = answerDF['健康程度'].values.tolist()
                elif xxx == '年龄':
                    df['年龄划分'] = pd.cut(df[xxx], [0, 20, 40, 60, 80, 100, 120],
                                        labels=['20岁以下', '20~40岁', '40~60岁', '60~80岁', '80~100岁', '100岁以上'])
                    answerDF = df.groupby('年龄划分').agg({'id': 'count'}).reset_index()
                    OptionIDList = answerDF['年龄划分'].values.tolist()
                else:
                    answerDF = df.groupby(xxx).agg({'id': 'count'}).reset_index()[:10]
                    OptionIDList = answerDF[xxx].values.tolist()
                PatientIDList = answerDF['id'].values.tolist()
                for i in range(0, len(OptionIDList)):
                    yield {"Option": OptionIDList[i],
                           "Count": PatientIDList[i], "Proportion": '%.2f' % (PatientIDList[i] / length * 100)}

            temp["options"] = inner_lop(obj['caption'])
            yield temp

    return render(request, 'analysis.html', {"form_list": inner(), "title": title})


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
                new_question_obj = models.Question.objects.create(caption=caption, ct=ct, questionnaire_id=pid,
                                                                  part_id=part_id)
                if ct == 2:
                    for op in options:
                        models.Option.objects.create(question=new_question_obj, name=op.get("name"),
                                                     score=op.get("score"))
            # 否则表示要更新
            else:
                models.Question.objects.filter(id=qid).update(caption=caption, ct=ct, questionnaire_id=pid,
                                                              part_id=part_id)
                if not options:  # 如果没有选项表示要删除选项
                    models.Option.objects.filter(question_id=qid).delete()
                else:
                    for op in options:
                        models.Option.objects.filter(question_id=qid).update(name=op.get("name"), score=op.get("score"),
                                                                             question_id=qid)
        return HttpResponse("ok")


def login(request):
    if request.method == 'POST':
        user = models.Doctor.objects.filter(name=request.POST.get("name"), pwd=request.POST.get("password")).first()
        if user:
            request.session["username"] = user.name
            request.session["id"] = user.id
            request.session["admin"] = "0"
            return redirect("/index/")
    return render(request, "login.html", )


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
