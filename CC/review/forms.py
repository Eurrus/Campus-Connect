from django import forms
from review.models import FlagPost
class FlagQuestionForm(forms.ModelForm):
	class Meta:
		model = FlagPost
		fields = ['actions_Flag_Q']
		widgets = {
			'actions_Flag_Q': forms.RadioSelect()
		}