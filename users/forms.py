# users/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm): 

	class Meta(UserCreationForm.Meta):
		model = CustomUser
		fields = UserCreationForm.Meta.fields

class SignUpForm(UserCreationForm):
	first_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
	last_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
	email = forms.EmailField(max_length=254, help_text='Required, so we can ensure your account is working.')

	class Meta:
		model = CustomUser
		fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2',)

class CustomUserChangeForm(UserChangeForm):

	class Meta:
		model = CustomUser
		fields = UserChangeForm.Meta.fields