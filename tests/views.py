import datetime

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView, DetailView
from django.views.generic.detail import SingleObjectMixin

from models import Test, Page, PageInTest, QuestionAnswer, TestResult


class ChooseTestView(ListView):
    model = Test


class QuestionsOnPageView(SingleObjectMixin, ListView):
    template_name = 'tests/page.html'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=Page.objects.all())
        return super(QuestionsOnPageView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(QuestionsOnPageView, self).get_context_data(**kwargs)
        context['page'] = self.object
        return context

    def get_queryset(self):
        return self.object.questions.all()


class TestView(DetailView):
    model = Test
    template_name = 'tests/test.html'


class ResultsView(DetailView):
    model = TestResult
    template_name = 'tests/results.html'
    context_object_name = 'result'

    def get_context_data(self, **kwargs):
        context = super(ResultsView, self).get_context_data(**kwargs)

        questions_with_answers = dict()

        for qa in context['result'].question_answers.all():
            correct = False
            if qa.score > 0:
                correct = True
            if qa.question in questions_with_answers:
                questions_with_answers[qa.question].append((qa.answer, correct))
            else:
                questions_with_answers[qa.question] = [(qa.answer, correct)]

        # list of tuples containing question, answers like:
        # [(q1, [(a11, correct), (a12, correct)]), (q2, [(a21, correct)])]
        result = []
        for k, v in questions_with_answers.items():
            result.append((k, v))
        context['questions_with_answers'] = result

        return context


class PageDetailView(DetailView):
    model = Page
    template_name = 'tests/page_detail.html'
    pk_url_kwarg = 'page_id'
    context_object_name = 'page'

    def get_context_data(self, **kwargs):
        context = super(PageDetailView, self).get_context_data(**kwargs)
        context['test'] = self.test
        page_index = PageInTest.objects.get(test=self.test, page=context['page']).page_index
        context['page_index'] = page_index
        total_pages = self.test.pages.count()
        context['total_pages'] = total_pages
        if page_index > 1:
            context['prev_page_id'] = PageInTest.objects.get(test=self.test, page_index=page_index - 1).id
        if page_index < total_pages:
            context['next_page_id'] = PageInTest.objects.get(test=self.test, page_index=page_index + 1).id
        else:
            context['next_page_id'] = 1000

        return context

    def get_object(self, queryset=None):

        test_id = self.kwargs['test_id']
        page_id = self.kwargs['page_id']

        self.test = Test.objects.get(pk=test_id)
        return self.test.pages.get(pk=page_id)


def process_page(request, test_id, page_id, next_page_id):
    if request.method == 'POST':
        try:
            result = TestResult.objects.get(test=test_id)
        except TestResult.DoesNotExist:
            result = None
            pass

        page = get_object_or_404(Page, pk=page_id)
        answers_to_questions_on_page = []
        questions = page.questions.all()
        try:
            for question in questions:
                choice = 'choice' + str(question.id)
                answer_choices = request.POST.getlist(choice)
                if not answer_choices:
                    raise KeyError
                for answer_choice in answer_choices:
                    qa = QuestionAnswer.objects.get(question=question.id, answer=answer_choice)
                    answers_to_questions_on_page.append(qa)

        except (KeyError, QuestionAnswer.DoesNotExist):
            test = Test.objects.get(pk=test_id)
            return render(request, 'tests/page_detail.html', {
                'test': test,
                'page': page,
                'page_index': PageInTest.objects.get(test=test_id, page=page_id).page_index,
                'total_pages': test.pages.count(),
                'next_page_id': next_page_id,
                'error_message': "You didn't answer to all questions.",
            })
        else:
            if result:
                # remove previous answers_to_questions_on_page for same questions
                to_remove = []
                for qa in result.question_answers.all():
                    if qa.question in questions:
                        to_remove.append(qa)
                for qa in to_remove:
                    result.question_answers.remove(qa)

                for qa in answers_to_questions_on_page:
                    result.question_answers.add(qa)

                result.save()
            else:
                result = TestResult(person='Ana', test=Test.objects.get(pk=test_id),
                                    date_taken=datetime.date.today())
                result.save()
                result.question_answers = answers_to_questions_on_page

            # Always return an HttpResponseRedirect after successfully dealing
            # with POST data. This prevents data from being posted twice if a
            # user hits the Back button.
            if int(next_page_id) == 1000:
                # end of test
                return HttpResponseRedirect(reverse('tests:results', args=(result.id,)))
            else:
                redirect_to = reverse('tests:test', args=(test_id, next_page_id))
                return HttpResponseRedirect(redirect_to)

    else:
        # if not POST
        # return render(request, 'tests/page_detail.html', {
        # 'test_id': test_id,
        #     'page_id': page_id
        # })
        redirect_to = reverse('tests:test', args=(test_id, page_id))
        return HttpResponseRedirect(redirect_to)
