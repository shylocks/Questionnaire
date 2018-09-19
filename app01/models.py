# -*- coding: utf-8 -*-
from django.db import models

# Create your models here.


class Patient(models.Model):
    '''
    病人表
    '''
    id = models.IntegerField(verbose_name="id", primary_key=True)
    name = models.CharField(max_length=16,verbose_name="姓名")
    sex = models.CharField(max_length=5, verbose_name="性别")
    age = models.IntegerField(verbose_name="年龄")
    idcard = models.CharField(verbose_name="身份证号", max_length=64)
    nation = models.CharField(verbose_name="名族", max_length=64)
    native_place = models.CharField(verbose_name="籍贯", max_length=64)
    education = models.CharField(verbose_name="教育程度", max_length=64)
    marriage = models.CharField(verbose_name="婚姻状况", max_length=64)
    children = models.CharField(verbose_name="子女数", max_length=64)
    longest_job = models.CharField(verbose_name="最长工作", default="", max_length=64)
    family_medical_history = models.CharField(verbose_name="家族病史", default="", max_length=64)

    class Meta:
        verbose_name_plural = "病人表"

    def __str__(self):
        return self.name


class Admin(models.Model):
    '''
    管理员表
    '''
    id = models.CharField(verbose_name="用户ID",max_length=16,primary_key=True)
    name = models.CharField(verbose_name="用户姓名",max_length=16)
    pwd = models.CharField(verbose_name="密码",max_length=16)

    class Meta:
        verbose_name_plural = "管理员表"

    def __str__(self):
        return self.name


class Hospital(models.Model):
    '''
    医院表
    '''
    id = models.CharField(verbose_name="医院ID", max_length=16,primary_key=True)
    name = models.CharField(verbose_name="医院名称", max_length=40)
    description = models.CharField(verbose_name="描述", max_length=40)

    class Meta:
        verbose_name_plural = "医院表"

    def __str__(self):
        return self.name


class Doctor(models.Model):
    '''
    医生表
    '''
    id = models.CharField(verbose_name="用户ID", max_length=16,primary_key=True)
    name = models.CharField(verbose_name="用户姓名", max_length=16)
    pwd = models.CharField(verbose_name="密码", max_length=16)
    position = models.CharField(verbose_name="职位",max_length=16)
    hospital = models.ForeignKey(verbose_name="医院ID",to="Hospital", on_delete=models.CASCADE)
    class Meta:
        verbose_name_plural = "医生表"

    def __str__(self):
        return self.name


class Questionnaire(models.Model):
    '''
    问卷表
    '''
    title = models.CharField(verbose_name="问卷标题",max_length=128)
    finished_num = models.IntegerField(verbose_name="参与人数",default=0)

    class Meta:
        verbose_name_plural = "问卷表"

    def __str__(self):
        return self.title


class Question(models.Model):
    '''
    问题表
    '''
    caption = models.CharField(verbose_name="问题标题",max_length=64)
    question_type = (
        (1,"填空评分"),
        (2,"问答评分"),
        (3,"备用"),
    )
    part_id = models.IntegerField(verbose_name="所属部分")
    ct = models.IntegerField(choices=question_type)
    questionnaire = models.ForeignKey(to="Questionnaire",on_delete=models.CASCADE)
    picture = models.BinaryField(verbose_name="图片数据")
    class Meta:
        verbose_name_plural = "问题表"
    def __str__(self):
        return self.caption


class Option(models.Model):
    '''
   单选题的选项
    '''
    name = models.CharField(verbose_name="选项名称",max_length=32)
    score = models.IntegerField(verbose_name="选项对应的分值")
    question = models.ForeignKey(to="Question",on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "单选题的选项"

    def __str__(self):
        return self.name


class Part(models.Model):
    '''
   Part表
    '''
    id = models.IntegerField(verbose_name="partid",primary_key=True)
    questionnaire = models.ForeignKey(to="Questionnaire",on_delete=models.CASCADE)
    part_id = models.IntegerField(verbose_name="partid2")
    description = models.CharField(verbose_name="描述",max_length=255)

    class Meta:
        verbose_name_plural = "Part表"

    def __str__(self):
        return self.name


class Answer(models.Model):
    '''
    答案
    '''
    user = models.ForeignKey(Patient,verbose_name="回答者",on_delete=models.CASCADE)
    question = models.ForeignKey(to='Question',verbose_name="问题",on_delete=models.CASCADE)
    content = models.CharField(verbose_name="答案内容",max_length=255,null=True,blank=True)
    option = models.ForeignKey(to="Option",null=True,blank=True,on_delete=models.CASCADE)
    val = models.IntegerField(null=True,blank=True)

    class Meta:
        verbose_name_plural = "答案表"