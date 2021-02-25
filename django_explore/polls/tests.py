import  datetime
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import Question, Choice

class QuestionModelTests(TestCase):
    
    def test_was_published_recently_with_future_questions(self):
        future_time = timezone.now() + datetime.timedelta(seconds = 1)
        future_question = Question(pub_date = future_time)
        self.assertIs(future_question.was_published_recently(), False)
    
    def test_was_published_recently_with_old_questions(self):
        past_time = timezone.now() - datetime.timedelta(days = 1, seconds = 1)
        past_question = Question(pub_date = past_time)
        self.assertIs(past_question.was_published_recently(), False)
    
    def test_was_published_recently_with_recent_questions(self):
        recent_time = timezone.now() - datetime.timedelta(hours = 23)
        recent_question = Question(pub_date = recent_time)
        self.assertIs(recent_question.was_published_recently(), True)

def create_question(question_text, days):
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text= question_text, pub_date = time)

class QuestionIndexViewTests(TestCase):

    def test_no_questions(self):
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['question_list'], [])

    def test_past_question(self):
        create_question("A Past Question", -30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['question_list'],
            ['<Question: A Past Question>']
        )

    def test_future_question(self):
        create_question("Future question.", 30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['question_list'], [])

    def test_future_question_and_past_question(self):
        create_question("Past question.", -30)
        create_question("Future question.", 30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['question_list'],
            ['<Question: Past question.>']
        )

    def test_two_past_questions(self):
        create_question("Past question 1.", -30)
        create_question("Past question 2.", -5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['question_list'],
            ['<Question: Past question 2.>', '<Question: Past question 1.>']
        )

class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        future_question = create_question(question_text='Future question.', days=5)
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        past_question = create_question(question_text='Past Question.', days=-5)
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)

class QuestionResultViewTests(TestCase):
    def test_future_question(self):
        future_question = create_question('Future question.', 5)
        url = reverse('polls:results', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        past_question = create_question('Past Question.', -5)
        choice = past_question.choice_set.create(choice_text="A Choice.")
        url = reverse('polls:results', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, choice.choice_text)