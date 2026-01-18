from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from django.conf import settings
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None

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
            self.user = user
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
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = False

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

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password:
            validate_password(password, self.instance if self.instance.pk else None)
        return password

    def clean_password2(self):
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')
        if password and password2 and password != password2:
            raise ValidationError('Пароли не совпадают')
        return password2

    @transaction.atomic
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
            if not self.is_bound:
                self.fields['email'].initial = self.user.email
                self.fields['first_name'].initial = self.user.first_name or ''

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar:
            max_size = 5 * 1024 * 1024  
            if avatar.size > max_size:
                raise ValidationError(f'Размер файла не должен превышать {max_size // (1024 * 1024)}MB')
        return avatar

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if self.user and User.objects.filter(email=email).exclude(pk=self.user.pk).exists():
            raise ValidationError('Пользователь с таким email уже существует')
        return email

    @transaction.atomic
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
        
        tag_names = [tag.strip() for tag in tags_str.split() if tag.strip()]
        
        max_tags = 5
        if len(tag_names) > max_tags:
            raise ValidationError(f'Можно указать не более {max_tags} тегов')
        
        max_tag_length = 50  
        for tag_name in tag_names:
            if len(tag_name) > max_tag_length:
                raise ValidationError(f'Тег "{tag_name}" слишком длинный (максимум {max_tag_length} символов)')
        
        return tags_str

    @transaction.atomic
    def save(self, commit=True, author=None):
        question = super().save(commit=False)
        if author:
            question.author = author
        if commit:
            question.save()
            tags_str = self.cleaned_data.get('tags', '')
            tag_names = [tag.strip().lower() for tag in tags_str.split() if tag.strip()]
            
            existing_tags = {tag.name: tag for tag in Tag.objects.filter(name__in=tag_names)}
            
            tags_to_create = []
            for tag_name in tag_names:
                if tag_name not in existing_tags:
                    tags_to_create.append(Tag(name=tag_name))
            
            if tags_to_create:
                Tag.objects.bulk_create(tags_to_create, ignore_conflicts=True)
                created_tags = Tag.objects.filter(name__in=[t.name for t in tags_to_create])
                for tag in created_tags:
                    existing_tags[tag.name] = tag
            
            question.tags.set([existing_tags[tag_name] for tag_name in tag_names])
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

    def clean_text(self):
        text = self.cleaned_data.get('text', '')
        max_length = 10000 
        if len(text) > max_length:
            raise ValidationError(f'Текст ответа не должен превышать {max_length} символов')
        return text

    def save(self, commit=True, question=None, author=None):
        answer = super().save(commit=False)
        if question:
            answer.question = question
        if author:
            answer.author = author
        if commit:
            answer.save()
        return answer