from django import forms
class FlagQuestionForm(forms.ModelForm):
	# like = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect)

	class Meta:
		model = FlagPost
		fields = ['actions_Flag_Q']
		widgets = {
			'actions_Flag_Q': forms.RadioSelect()
		}