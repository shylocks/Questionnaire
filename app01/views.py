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
from .forms import QuestionnaireForm, QuestionModelForm, OptionModelForm, DoctorForm, PatientForm, HospitalForm


# Create your views here.
def index(request):
    return render(request, 'index.html', locals())


def questionnaires(request):
    if request.method == "GET":
        pars = parse_qs(request.GET.urlencode())
        if pars.get('method'):
            if pars['method'][0] == 'delete':
                models.Questionnaire.objects.filter(id=pars['id'][0]).delete()
            if pars['method'][0] == 'view_static':
                ques = models.Questionnaire.objects.filter(id=pars['id'][0]).first()
                question_list = models.Question.objects.filter(questionnaire_id=ques.id)
                answer_list = models.Answer.objects.all()
                question_id_list=[]
                for question in question_list:
                    question_id_list.append(question.id)
                participant_id_list = []
                for answer in answer_list:
                    if answer.user_id not in participant_id_list:
                        participant_id_list.append(answer.user_id)
                score_list = []
                for participant_id in participant_id_list:
                    this_score = 0
                    this_answer_list = models.Answer.objects.filter(user_id=participant_id)
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

                return render(request, 'ques_static.html', locals())
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
    Doctor_list = models.Doctor.objects.all()

    return render(request, 'doctor.html', locals())


def hospital(request):
    if request.method == "GET":
        pars = parse_qs(request.GET.urlencode())
        if pars.get('method'):
            if pars['method'][0] == 'delete':
                models.Hospital.objects.filter(id=pars['id'][0]).delete()
    Hospital_list = models.Hospital.objects.all()
    return render(request, 'hospital.html', locals())


def patient(request):
    if request.method == "GET":
        pars = parse_qs(request.GET.urlencode())
        if pars.get('method'):
            if pars['method'][0] == 'delete':
                models.Patient.objects.filter(id=pars['id'][0]).delete()
            elif pars['method'][0] == 'further':
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
                    this_answer_list = models.Answer.objects.filter(user_id=pars['id'][0])
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
                    participant_list.append(tmp)
                Patient_list = models.Patient.objects.filter(id=pars['id'][0])
                Patient = Patient_list[0]
                return render(request, 'patient_info.html', locals())
    elif request.is_ajax():
        id = request.POST.get("id")
        name = request.POST.get("name")
        sex = request.POST.get("sex")
        age = request.POST.get("age")
        idcard = request.POST.get("idcard")
        nation = request.POST.get("nation")
        native_place = request.POST.get("native_place")
        education = request.POST.get("education")
        marriage = request.POST.get("marriage")
        children = request.POST.get("children")
        longest_job = request.POST.get("longest_job","无")
        family_medical_history = request.POST.get("family_medical_history","无")
        models.Patient.objects.filter(id=id).update(name=name, sex=sex, age=age, idcard=idcard,
                                                    nation=nation, native_place=native_place,
                                                    education=education, marriage=marriage,
                                                    children=children, longest_job=longest_job,
                                                    family_medical_history=family_medical_history)
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


def add_patient(request):
    if request.method == "GET":
        return render(request, 'add_patient.html')
    elif request.is_ajax():
        id = len(models.Patient.objects.all())+1
        name = request.POST.get("name")
        sex = request.POST.get("sex")
        age = request.POST.get("age")
        idcard = request.POST.get("idcard")
        nation = request.POST.get("nation")
        native_place = request.POST.get("native_place")
        education = request.POST.get("education")
        marriage = request.POST.get("marriage")
        children = request.POST.get("children")
        longest_job = request.POST.get("longest_job", "无")
        family_medical_history = request.POST.get("family_medical_history", "无")
        models.Patient.objects.create(id=id,name=name, sex=sex, age=age, idcard=idcard,
                                                    nation=nation, native_place=native_place,
                                                    education=education, marriage=marriage,
                                                    children=children, longest_job=longest_job,
                                                    family_medical_history=family_medical_history)

    Patient_list = models.Patient.objects.all()
    return render(request, 'patient.html', locals())


def add_hospital(request):
    if request.method == "GET":
        form = HospitalForm()
        return render(request, 'add_hospital.html', {"form": form})
    else:
        form = HospitalForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data.get("name")
            description = form.cleaned_data.get("description")
            id = 1 + len(models.Hospital.objects.all())
            models.Hospital.objects.create(id=id, name=name, description=description)
            return redirect("/hospital/")
        else:
            return render(request, 'add_hospital.html', {"form": form})


def add_doctor(request):
    if request.method == "GET":
        form = DoctorForm()
        return render(request, 'add_doctor.html', {"form": form})
    else:
        form = DoctorForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data.get("name")
            id = 10001 + len(models.Doctor.objects.all())
            hospital = form.cleaned_data.get("hospital")
            position = form.cleaned_data.get("position")
            models.Doctor.objects.create(id=id, name=name, pwd="123456", hospital_id=hospital,position=position)
            return redirect("/doctor/")
        else:
            return render(request, 'add_doctor.html', {"form": form})


def view_questionnaire(request,pid):
    if request.method == "GET":
        pars = parse_qs(request.GET.urlencode())
        if pars.get("method"):
            if pars['method'][0] == 'delete':
                questionID = pars['QuestionID'][0]
                models.Question.objects.filter(id=questionID).delete()
            if pars['method'][0] == 'viewPart':
                partID = pars['PartID'][0]
                part = models.Part.objects.filter(id=partID).first()
                return render(request, 'PartModel.html', locals())
    elif request.is_ajax():
        item = json.loads(request.body.decode("utf-8"))
        print(item.get("id"))
        models.Part.objects.filter(id=item.get("id")).update(description=item.get("description"))
    qid = int(pid)
    Questionnaire = models.Questionnaire.objects.filter(id=pid).first()
    question_list = models.Question.objects.filter(questionnaire_id=pid)
    parts = []
    option_list = models.Option.objects.all()
    for ques in question_list:
        if ques.part_id not in parts:
            parts.append(ques.part_id)
    parts.sort()
    part_list = models.Part.objects.all()
    return render(request, 'questionnaire.html', locals())


def add_questionnaire(request):
    if request.method == "GET":
        form = QuestionnaireForm()
        return render(request, 'add_questionnaire.html', {"form": form})
    else:
        form = QuestionnaireForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data.get("title")
            models.Questionnaire.objects.create(title=title)
            return redirect("/ques/")
        else:
            return render(request, 'add_questionnaire.html', {"form": form})


def edit_doctor(request, uid):
    Doctor_list = models.Doctor.objects.all()
    return render(request, 'doctor.html', locals())


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
                    models.Option.objects.filter(question_id=qid).delete()
                    for op in options:
                        models.Option.objects.create(name=op.get("name"), score=op.get("score"), question_id=qid)
        return HttpResponse("ok")


def func(content):
    if len(content) < 15:
        raise ValidationError("长度不得少于15个字符")


def test(request):
    return render(request, "test.html", )


def question(request):
    if request.method == "GET":
        pars = parse_qs(request.GET.urlencode())
        if pars['method'][0] == 'view':
            questionID = pars['QuestionID'][0]
            question = models.Question.objects.filter(id=questionID).first()
            optionlist = models.Option.objects.filter(question_id=questionID)
            return render(request, "QuestionModel.html",locals())
    elif request.is_ajax():
        item = json.loads(request.body.decode("utf-8"))
        print(item)
        qid = item.get("id")
        caption = item.get("caption")
        ct = item.get("ct")
        options = item.get("options")
        part_id = item.get("part_id")
        models.Question.objects.filter(id=qid).update(caption=caption, ct=ct, part_id=part_id)
        models.Option.objects.filter(question_id=qid).delete()
        for op in options:
            #id = len(models.Patient.objects.all()) + 1
            models.Option.objects.create(name=op.get("name"), score=op.get("score"), question_id=qid)
        return HttpResponse("ok")
    return render(request, "QuestionModel.html", )


def score(request, ques_id, cls_id, ):
    stu_id = request.session.get("id")  # 从session中取出当前登录用户的ID
    if not stu_id:
        return redirect("/student_login/")

    # 判断当前登录的用户是否是要答卷的班级的学生

    stu_obj = models.Doctor.objects.filter(id=stu_id, cls_id=cls_id).count()

    if not stu_obj:
        return HttpResponse("对不起，您不是本次问卷调查对象")

    # 判断是否已经提交过问卷答案

    has_join = models.Answer.objects.filter(user_id=stu_id, question__questionnaire_id=ques_id)
    if has_join:
        return HttpResponse("对不起，您已经参与过本次问卷，不可重复参与")

    # 展示当前问卷下的所有问题

    # 获取当前问卷的所有问题
    question_list = models.Question.objects.filter(questionnaire_id=ques_id)
    field_dict = {}

    for que in question_list:

        if que.ct == 1:

            field_dict["val_%s" % que.id] = fields.ChoiceField(
                label=que.caption,
                error_messages={"required": "必填"},
                widget=widgets.RadioSelect,
                choices=[(i, i) for i in range(1, 11)]

            )
        elif que.ct == 2:
            field_dict["option_id_%s" % que.id] = fields.ChoiceField(
                label=que.caption,
                error_messages={"required": "必填"},
                widget=widgets.RadioSelect,
                ##这里数据表option中的score是不需要给用户看到的
                choices=models.Option.objects.filter(question_id=que.id).values_list("id", "name")
            )
        else:
            field_dict["content_%s" % que.id] = fields.CharField(
                label=que.caption,
                error_messages={"required": "必填"},
                widget=widgets.Textarea(attrs={"class": "form-control", "rows": "2", "cols": "60"}),
                validators=[func, ]  # 这里可以写正则，也可以自定义函数放在这里
            )
    myForm = type("myTestForm", (Form,), field_dict)  # 动态生成类，参数分别是类名，继承的对象，字段
    if request.method == "GET":
        form = myForm()
        return render(request, "score.html", {"question_list": question_list, "form": form})
    else:
        form = myForm(request.POST)
        if form.is_valid():
            obj_list = []
            for key, v in form.cleaned_data.items():
                print(key, v)
                key, qid = key.rsplit("_", 1)  # 从右边切，切一次
                answer_dict = {"user_id": stu_id, "question_id": qid, key: v}
                print(answer_dict)
                obj_list.append(models.Answer(**answer_dict))
            models.Answer.objects.bulk_create(obj_list)  # 批量插入
            return HttpResponse("感谢您的参与")

        return render(request, "score.html", {"question_list": question_list, "form": form})
'''
 for i in questionnaire_list:
        v = models.Answer.objects.filter(question__questionnaire=i).distinct().annotate(c=Count("user_id")).values(
            "c").count()
        print(v)
    i.stu_num = v'''