# -*- coding: utf-8 -*-
from django.db import models


# Create your models here.


class Patient(models.Model):
    '''
    病人表
    '''
    gender_type = (
        (1, "男性"),
        (2, "女性"),
    )
    nation_type = (
        (1, "汉族"),
        (2, "蒙古族"),
        (3, "回族"),
        (4, "藏族"),
        (5, "维吾尔族"),
        (6, "苗族"),
        (7, "彝族"),
        (8, "壮族"),
        (9, "布依族"),
        (10, "朝鲜族"),
        (11, "满族"),
        (12, "侗族"),
        (13, "瑶族"),
        (14, "白族"),
        (15, "土家族"),
        (16, "哈尼族"),
        (17, "哈萨克族"),
        (18, "傣族"),
        (19, "黎族"),
        (20, "傈僳族"),
        (21, "佤族"),
        (22, "畲族"),
        (23, "高山族"),
        (24, "拉祜族"),
        (25, "水族"),
        (26, "东乡族"),
        (27,"纳西族"),
        (28, "景颇族"),
        (29, "柯尔克孜族"),
        (30, "土族"),
        (31, "达斡尔族"),
        (32, "仫佬族"),
        (33, "羌族"),
        (34, "布朗族"),
        (35, "撒拉族"),
        (36, "毛难族"),
        (37, "仡佬族"),
        (38, "锡伯族"),
        (39, "阿昌族"),
        (40, "普米族"),
        (41, "塔吉克族"),
        (42, "怒族"),
        (43, "乌孜别克族"),
        (44, "俄罗斯族"),
        (45, "鄂温克族"),
        (46, "崩龙族"),
        (47, "保安族"),
        (48, "裕固族"),
        (49, "京族"),
        (50, "塔塔尔族"),
        (51, "独龙族"),
        (52, "鄂伦春族"),
        (53, "赫哲族"),
        (54, "门巴族"),
        (55, "珞巴族"),
        (56, "基诺族"),
        (97, "其他"),
        (98, "外国血统"),
    )
    education_type = (
        (1, "小学"),
        (2, "初中"),
        (3, "高中"),
        (4, "大学"),
        (5, "研究生"),
        (6, "无")
    )
    marriage_type = (
        (1, "已婚"),
        (2, "曾今离异"),
        (3, "未婚"),
        (4, "离异"),
        (5, "丧偶"),
    )
    children_type = (
        (0, 0),
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
        (5, 5),
        (6, 6),
        (7, "更多")
    )
    id = models.IntegerField(verbose_name="id", primary_key=True, blank=True)
    name = models.CharField(max_length=16, verbose_name="姓名")
    gender = models.IntegerField(choices=gender_type, verbose_name="性别")
    age = models.IntegerField(verbose_name="年龄")
    idcard = models.CharField(verbose_name="身份证号", max_length=64)
    nation = models.IntegerField(choices=nation_type, verbose_name="名族")
    native_place = models.CharField(verbose_name="籍贯",max_length=64)
    education = models.IntegerField(choices=education_type, verbose_name="教育程度")
    marriage = models.IntegerField(choices=marriage_type, verbose_name="婚姻状况")
    children = models.IntegerField(choices=children_type, verbose_name="子女数")
    longest_job = models.CharField(verbose_name="最长工作", default="", max_length=64, blank=True)
    family_medical_history = models.CharField(verbose_name="家族病史", default="", max_length=64, blank=True)

    class Meta:
        verbose_name_plural = "病人表"

    def __str__(self):
        return self.name


class Admin(models.Model):
    '''
    管理员表
    '''
    id = models.CharField(verbose_name="用户ID", max_length=16, primary_key=True)
    name = models.CharField(verbose_name="用户姓名", max_length=16)
    pwd = models.CharField(verbose_name="密码", max_length=16)

    class Meta:
        verbose_name_plural = "管理员表"

    def __str__(self):
        return self.name


class Hospital(models.Model):
    '''
    医院表
    '''
    id = models.CharField(verbose_name="医院ID", max_length=16, primary_key=True)
    name = models.CharField(verbose_name="医院名称", max_length=40)
    description = models.CharField(verbose_name="描述", max_length=40)

    class Meta:
        verbose_name_plural = "医院表"

    def __str__(self):
        return self.name


class Res(models.Model):
    '''
    回答表
    '''
    id = models.IntegerField(verbose_name="回答ID", primary_key=True)
    time_stamp = models.CharField(verbose_name="UNIX时间戳", max_length=64)
    patient = models.ForeignKey(to="Patient", verbose_name="病人ID", on_delete=None)
    doctor = models.ForeignKey(to="Doctor", verbose_name="医生ID", on_delete=None)
    questionnaire = models.ForeignKey(to="Questionnaire", verbose_name="问卷ID", on_delete=None)
    score = models.IntegerField(verbose_name="得分")


    class Meta:
        verbose_name_plural = "回答表"

    def __str__(self):
        return self.id


class Doctor(models.Model):
    '''
    医生表
    '''
    id = models.CharField(verbose_name="用户ID", max_length=16, primary_key=True)
    name = models.CharField(verbose_name="用户姓名", max_length=16)
    pwd = models.CharField(verbose_name="密码", max_length=16)
    position = models.CharField(verbose_name="职位", max_length=16)
    hospital = models.ForeignKey(verbose_name="医院ID", to="Hospital", on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "医生表"

    def __str__(self):
        return self.name


class Questionnaire(models.Model):
    '''
    问卷表
    '''
    title = models.CharField(verbose_name="问卷标题", max_length=128)
    finished_num = models.IntegerField(verbose_name="参与人数", default=0)

    class Meta:
        verbose_name_plural = "问卷表"

    def __str__(self):
        return self.title


class Question(models.Model):
    '''
    问题表
    '''
    caption = models.CharField(verbose_name="问题标题", max_length=64)
    question_type = (
        (1, "填空评分"),
        (2, "问答评分"),
        (3, "备用"),
    )
    part_id = models.IntegerField(verbose_name="所属部分")
    ct = models.IntegerField(choices=question_type)
    questionnaire = models.ForeignKey(to="Questionnaire", on_delete=models.CASCADE)
    picture = models.BinaryField(verbose_name="图片数据")

    class Meta:
        verbose_name_plural = "问题表"

    def __str__(self):
        return self.caption


class Option(models.Model):
    '''
   单选题的选项
    '''
    name = models.CharField(verbose_name="选项名称", max_length=32)
    score = models.IntegerField(verbose_name="选项对应的分值")
    question = models.ForeignKey(to="Question", on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "单选题的选项"

    def __str__(self):
        return self.name


class Part(models.Model):
    '''
   Part表
    '''
    id = models.IntegerField(verbose_name="partid", primary_key=True)
    questionnaire = models.ForeignKey(to="Questionnaire", on_delete=models.CASCADE)
    part_id = models.IntegerField(verbose_name="partid2")
    description = models.CharField(verbose_name="描述", max_length=255)

    class Meta:
        verbose_name_plural = "Part表"

    def __str__(self):
        return self.id


class Answer(models.Model):
    '''
    答案
    '''
    patient = models.ForeignKey(to='Patient', verbose_name="回答者", on_delete=models.CASCADE)
    question = models.ForeignKey(to='Question', verbose_name="问题", on_delete=models.CASCADE)
    content = models.CharField(verbose_name="答案内容", max_length=255, null=True, blank=True)
    option = models.ForeignKey(to="Option", null=True, blank=True, on_delete=models.CASCADE)
    val = models.IntegerField(null=True, blank=True)
    res = models.ForeignKey(to="Res", on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "答案表"
