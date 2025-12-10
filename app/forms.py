from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Question, Answer, Tag, Profile


class LoginForm(forms.Form):
    username = forms.CharField(
        label='Имя пользователя',
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите имя пользователя',
            'autofocus': True
        })
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if user is None:
                raise ValidationError('Неверное имя пользователя или пароль')
            if not user.is_active:
                raise ValidationError('Аккаунт неактивен')
        return cleaned_data


class SignupForm(forms.ModelForm):
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        }),
        min_length=8
    )
    password2 = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Повторите пароль'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите имя пользователя',
                'autofocus': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите email'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите имя'
            }),
        }
        labels = {
            'username': 'Имя пользователя',
            'email': 'Email',
            'first_name': 'Имя',
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError('Пользователь с таким именем уже существует')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Пользователь с таким email уже существует')
        return email

    def clean_password2(self):
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')
        if password and password2 and password != password2:
            raise ValidationError('Пароли не совпадают')
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            Profile.objects.get_or_create(user=user)
        return user


class ProfileEditForm(forms.ModelForm):
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите email'
        })
    )
    first_name = forms.CharField(
        label='Полное имя',
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите полное имя'
        })
    )

    class Meta:
        model = Profile
        fields = ['avatar']
        widgets = {
            'avatar': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }
        labels = {
            'avatar': 'Аватар',
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            # Устанавливаем initial значения только если форма не bound (GET запрос)
            if not self.is_bound:
                self.fields['email'].initial = self.user.email
                self.fields['first_name'].initial = self.user.first_name or ''

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if self.user and User.objects.filter(email=email).exclude(pk=self.user.pk).exists():
            raise ValidationError('Пользователь с таким email уже существует')
        return email

    def save(self, commit=True):
        profile = super().save(commit=False)
        if self.user:
            self.user.email = self.cleaned_data['email']
            self.user.first_name = self.cleaned_data.get('first_name', '')
            if commit:
                self.user.save()
                profile.save()
        return profile


class QuestionForm(forms.ModelForm):
    tags = forms.CharField(
        label='Теги',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'python django web'
        }),
        help_text='Введите теги через пробел (например: python django web)'
    )

    class Meta:
        model = Question
        fields = ['title', 'text']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите заголовок вопроса',
                'autofocus': True
            }),
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 10,
                'placeholder': 'Опишите ваш вопрос подробно...'
            })
        }
        labels = {
            'title': 'Заголовок вопроса',
            'text': 'Текст вопроса',
        }

    def clean_tags(self):
        tags_str = self.cleaned_data.get('tags', '')
        if not tags_str.strip():
            raise ValidationError('Необходимо указать хотя бы один тег')
        return tags_str

    def save(self, commit=True, author=None):
        question = super().save(commit=False)
        if author:
            question.author = author
        if commit:
            question.save()
            # Обрабатываем теги
            tags_str = self.cleaned_data.get('tags', '')
            tag_names = [tag.strip().lower() for tag in tags_str.split() if tag.strip()]
            tags = []
            for tag_name in tag_names:
                tag, created = Tag.objects.get_or_create(name=tag_name)
                tags.append(tag)
            question.tags.set(tags)
        return question


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Введите ваш ответ здесь...',
                'autofocus': True
            })
        }
        labels = {
            'text': 'Текст ответа',
        }

    def save(self, commit=True, question=None, author=None):
        answer = super().save(commit=False)
        if question:
            answer.question = question
        if author:
            answer.author = author
        if commit:
            answer.save()
        return answer
