from django import forms
from .models import Task, TaskEvidence
from django.utils.html import strip_tags
from django.utils import timezone

class TaskForm(forms.ModelForm):
    due_date = forms.DateField(
        required=False,
        input_formats=['%Y-%m-%d', '%d/%m/%Y', '%d/%m/%y', '%d-%m-%Y'],
        widget=forms.DateInput(
            format='%Y-%m-%d',
            attrs={
                'type': 'date', 
                'class': 'w-full h-[42px] px-4 py-2 bg-white dark:bg-gray-900 text-gray-900 dark:text-white border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:border-orange-500'
            }
        ),
        error_messages={'invalid': 'Formato de data inválido. Use DD/MM/AAAA ou escolha no calendário.'}
    )

    photo = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'w-full h-[42px] px-4 py-2 bg-white dark:bg-gray-900 text-gray-900 dark:text-white border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:border-orange-500',
            'accept': 'image/*'
        }),
        error_messages={'invalid': 'Formato de imagem inválido.'}
    )

    class Meta:
        model = Task
        fields = ['title', 'description', 'priority', 'location', 'due_date',
                  'cep', 'logradouro', 'numero', 'complemento', 'bairro', 'cidade', 'estado']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full h-[42px] px-4 py-2 bg-white dark:bg-gray-900 text-gray-900 dark:text-white border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:border-orange-500', 'placeholder': 'Título da tarefa'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-4 py-2 bg-white dark:bg-gray-900 text-gray-900 dark:text-white border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:border-orange-500', 'rows': 4}),
            'priority': forms.Select(attrs={'class': 'w-full h-[42px] px-4 py-2 bg-white dark:bg-gray-900 text-gray-900 dark:text-white border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:border-orange-500'}),
            'location': forms.TextInput(attrs={'class': 'w-full h-[42px] px-4 py-2 bg-white dark:bg-gray-900 text-gray-900 dark:text-white border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:border-orange-500', 'placeholder': 'Ex: Sala 302, Corredor B...'}),
            'cep': forms.TextInput(attrs={'class': 'w-full h-[42px] px-4 py-2 bg-white dark:bg-gray-900 text-gray-900 dark:text-white border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:border-orange-500 mask-cep', 'placeholder': '00000-000', 'maxlength': '9', 'id': 'task_cep'}),
            'logradouro': forms.TextInput(attrs={'class': 'w-full h-[42px] px-4 py-2 bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-white border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:border-orange-500', 'readonly': 'readonly', 'id': 'task_logradouro'}),
            'numero': forms.TextInput(attrs={'class': 'w-full h-[42px] px-4 py-2 bg-white dark:bg-gray-900 text-gray-900 dark:text-white border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:border-orange-500', 'placeholder': 'Número', 'id': 'task_numero'}),
            'complemento': forms.TextInput(attrs={'class': 'w-full h-[42px] px-4 py-2 bg-white dark:bg-gray-900 text-gray-900 dark:text-white border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:border-orange-500', 'placeholder': 'Apto, sala, bloco...', 'id': 'task_complemento'}),
            'bairro': forms.TextInput(attrs={'class': 'w-full h-[42px] px-4 py-2 bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-white border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:border-orange-500', 'readonly': 'readonly', 'id': 'task_bairro'}),
            'cidade': forms.TextInput(attrs={'class': 'w-full h-[42px] px-4 py-2 bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-white border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:border-orange-500', 'readonly': 'readonly', 'id': 'task_cidade'}),
            'estado': forms.TextInput(attrs={'class': 'w-full h-[42px] px-4 py-2 bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-white border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:border-orange-500', 'readonly': 'readonly', 'id': 'task_estado', 'maxlength': '2'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['due_date'].widget.attrs['min'] = timezone.now().date().isoformat()

    def clean_due_date(self):
        due_date = self.cleaned_data.get('due_date')
        if due_date and due_date < timezone.now().date():
            # Permitir data no passado se for edição e a data não foi alterada
            if self.instance.pk and self.instance.due_date == due_date:
                return due_date
            raise forms.ValidationError("A data de vencimento não pode estar no passado.")
        return due_date

    def clean_title(self):
        return strip_tags(self.cleaned_data.get('title', '')).strip()

    def clean_description(self):
        return strip_tags(self.cleaned_data.get('description', '')).strip()

    def clean_location(self):
        return strip_tags(self.cleaned_data.get('location', '')).strip()

    def clean_cep(self):
        return strip_tags(self.cleaned_data.get('cep', '')).strip()

    def clean_numero(self):
        return strip_tags(self.cleaned_data.get('numero', '')).strip()

    def clean_complemento(self):
        return strip_tags(self.cleaned_data.get('complemento', '')).strip()

class TaskEvidenceForm(forms.ModelForm):
    class Meta:
        model = TaskEvidence
        fields = ['photo', 'description']
        widgets = {
            'photo': forms.FileInput(attrs={'class': 'w-full h-[42px] px-4 py-2 bg-white dark:bg-gray-900 text-gray-900 dark:text-white border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:border-orange-500'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-4 py-2 bg-white dark:bg-gray-900 text-gray-900 dark:text-white border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:border-orange-500', 'rows': 3}),
        }

    def clean_description(self):
        return strip_tags(self.cleaned_data.get('description', '')).strip()
