from django.db import models


class Answer(models.Model):
    text = models.CharField(max_length=200)

    def __unicode__(self):
        return self.text


class Question(models.Model):
    text = models.CharField(max_length=200)
    answer = models.ManyToManyField(Answer, through='QuestionAnswer')

    def __unicode__(self):
        return self.text


class QuestionAnswer(models.Model):
    question = models.ForeignKey(Question)
    answer = models.ForeignKey(Answer)
    score = models.SmallIntegerField()


class Page(models.Model):
    description = models.CharField(max_length=50)
    questions = models.ManyToManyField(Question, through='QuestionOnPage')

    def __unicode__(self):
        return self.description


class QuestionOnPage(models.Model):
    question = models.ForeignKey(Question)
    page = models.ForeignKey(Page)
    question_index = models.PositiveSmallIntegerField()


class Test(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    pages = models.ManyToManyField(Page, through='PageInTest')

    def __unicode__(self):
        return self.name


class PageInTest(models.Model):
    page = models.ForeignKey(Page)
    test = models.ForeignKey(Test)
    page_index = models.PositiveSmallIntegerField()


class TestResult(models.Model):
    person = models.CharField(max_length=50)
    test = models.ForeignKey(Test)
    date_taken = models.DateField()
    question_answers = models.ManyToManyField(QuestionAnswer)

    def __unicode__(self):
        return u'%s - %s' % (self.person, self.test.name)

