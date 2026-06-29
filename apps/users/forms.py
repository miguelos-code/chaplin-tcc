from django import forms
from django.contrib.auth.models import User
from django.utils.html import strip_tags

class UserRegistrationForm(forms.ModelForm):
    username = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg', 'maxlength': '30'}))
    email = forms.EmailField(max_length=254, widget=forms.EmailInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg', 'maxlength': '254'}))
    first_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg', 'maxlength': '150'}))
    password = forms.CharField(min_length=8, widget=forms.PasswordInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg', 'minlength': '8'}))
    password_confirm = forms.CharField(min_length=8, widget=forms.PasswordInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg', 'minlength': '8'}), label="Confirmar Senha")
    ROLE_CHOICES = [
        ('gestor', 'Gestor Predial (Anfitrião)'),
        ('lider', 'Líder de Equipe Técnica'),
        ('colaborador', 'Colaborador'),
    ]
    role = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'}))
    cpf = forms.CharField(max_length=14, widget=forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg mask-cpf', 'placeholder': '000.000.000-00'}))
    cnpj = forms.CharField(max_length=18, required=False, widget=forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg mask-cnpj', 'placeholder': '00.000.000/0000-00'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', "As senhas não coincidem.")
        return cleaned_data

    def clean_first_name(self):
        return strip_tags(self.cleaned_data.get("first_name", "")).strip()

    def clean_username(self):
        return strip_tags(self.cleaned_data.get("username", "")).strip()
    def clean_cpf(self):
        return strip_tags(self.cleaned_data.get("cpf", "")).strip()
    def clean_cnpj(self):
        return strip_tags(self.cleaned_data.get("cnpj", "")).strip()


class AdminUserCreateForm(forms.ModelForm):
    INPUT_CSS = 'w-full px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-orange-500 focus:outline-none dark:text-white'

    username = forms.CharField(max_length=30, label='Usuário', widget=forms.TextInput(attrs={'class': INPUT_CSS, 'placeholder': 'Nome de usuário'}))
    email = forms.EmailField(max_length=254, label='E-mail', widget=forms.EmailInput(attrs={'class': INPUT_CSS, 'placeholder': 'email@exemplo.com'}))
    first_name = forms.CharField(max_length=150, label='Nome', widget=forms.TextInput(attrs={'class': INPUT_CSS}))
    last_name = forms.CharField(max_length=150, label='Sobrenome', required=False, widget=forms.TextInput(attrs={'class': INPUT_CSS}))
    password = forms.CharField(min_length=8, label='Senha', widget=forms.PasswordInput(attrs={'class': INPUT_CSS, 'minlength': '8'}))
    password_confirm = forms.CharField(min_length=8, label='Confirmar Senha', widget=forms.PasswordInput(attrs={'class': INPUT_CSS, 'minlength': '8'}))

    ROLE_CHOICES = [
        ('colaborador', 'Colaborador'),
        ('lider', 'Líder de Equipe Técnica'),
        ('gestor', 'Gestor Predial (Anfitrião)'),
    ]
    role = forms.ChoiceField(choices=ROLE_CHOICES, label='Nível de Acesso', widget=forms.Select(attrs={'class': INPUT_CSS}))
    phone = forms.CharField(max_length=20, required=False, label='Telefone', widget=forms.TextInput(attrs={'class': INPUT_CSS + ' mask-phone', 'placeholder': '(11) 99999-9999'}))
    cpf = forms.CharField(max_length=14, required=False, label='CPF', widget=forms.TextInput(attrs={'class': INPUT_CSS + ' mask-cpf', 'placeholder': '000.000.000-00'}))
    cnpj = forms.CharField(max_length=18, required=False, label='CNPJ', widget=forms.TextInput(attrs={'class': INPUT_CSS + ' mask-cnpj', 'placeholder': '00.000.000/0000-00'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password']

    def clean(self):
        cleaned_data = super().clean()
        pw = cleaned_data.get("password")
        pw2 = cleaned_data.get("password_confirm")
        if pw and pw2 and pw != pw2:
            self.add_error('password_confirm', "As senhas não coincidem.")
        return cleaned_data

    def clean_first_name(self):
        return strip_tags(self.cleaned_data.get("first_name", "")).strip()

    def clean_last_name(self):
        return strip_tags(self.cleaned_data.get("last_name", "")).strip()

    def clean_username(self):
        return strip_tags(self.cleaned_data.get("username", "")).strip()

    def clean_phone(self):
        return strip_tags(self.cleaned_data.get("phone", "")).strip()

    def clean_cpf(self):
        return strip_tags(self.cleaned_data.get("cpf", "")).strip()

    def clean_cnpj(self):
        return strip_tags(self.cleaned_data.get("cnpj", "")).strip()
