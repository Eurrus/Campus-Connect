from .models import Question,Answer
from django import forms
class QuestionForm(forms.ModelForm):
	class Meta:
		model = Question
		fields = ['title','body']
class AnswerForm(forms.ModelForm):
	class Meta:
		model = Answer
		fields = ['body']
class EditAnswerForm(forms.ModelForm):
	class Meta:
		model = Answer
		fields = ['body']
class UpdateQuestion(forms.ModelForm):
	class Meta:
		model = Question
		fields = ['title','body','tags']