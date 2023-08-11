from django.contrib.auth.forms import UserCreationForm
from .models import User
from django import forms

class CreateAccountForm(UserCreationForm):
    email = forms.EmailField()
    stocks = forms.CharField()

    class Meta: #diz quem é o modelo que sera usado como referencia
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'stocks')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = None
        self.fields['email'].help_text = None
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None
        self.fields['stocks'].help_text = 'Enter the stock symbol you want to track. Separate with a comma, without spaces (ex: AAPL,AMZN,GOOG,...)'