from django import forms
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

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not User.objects.filter(username=username).exists():
            raise ValidationError('Пользователь с таким именем не существует')
        return username

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not password or len(password) < 1:
            raise ValidationError('Пароль не может быть пустым')
        return password


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
    avatar = forms.ImageField(
        label='Аватар',
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
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
        }
        labels = {
            'username': 'Имя пользователя',
            'email': 'Email',
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError('Пользователь с таким именем уже существует')
        
        if len(username) < 3:
            raise ValidationError('Имя пользователя должно содержать минимум 3 символа')
        
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
            user.save(update_fields=['username', 'email', 'password'])
            
            profile = Profile.objects.create(
                user=user,
                avatar=self.cleaned_data.get('avatar')
            )
            profile.save(update_fields=['avatar'])
            
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
        label='Имя',
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите ваше имя'
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
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        
        self.fields['email'].initial = self.user.email
        self.fields['first_name'].initial = self.user.first_name

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(pk=self.user.pk).exists():
            raise ValidationError('Пользователь с таким email уже существует')
        return email

    def save(self, commit=True):
        profile = super().save(commit=False)
        
        self.user.email = self.cleaned_data['email']
        self.user.first_name = self.cleaned_data['first_name']
        
        if commit:
            user_update_fields = ['email']
            if 'first_name' in self.changed_data:
                user_update_fields.append('first_name')
            
            self.user.save(update_fields=user_update_fields)
            profile.save()
        
        return profile


class QuestionForm(forms.ModelForm):
    tags = forms.CharField(
        label='Теги',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'python django web'
        }),
        help_text='Введите теги через пробел (например: python django web)',
        required=False
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

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if len(title) < 10:
            raise ValidationError('Заголовок должен содержать минимум 10 символов')
        return title

    def clean_text(self):
        text = self.cleaned_data.get('text')
        if len(text) < 20:
            raise ValidationError('Текст вопроса должен содержать минимум 20 символов')
        return text

    def clean_tags(self):
        tags_str = self.cleaned_data.get('tags', '').strip()
        if not tags_str:
            raise ValidationError('Необходимо указать хотя бы один тег')
        
        tag_names = [tag.strip().lower() for tag in tags_str.split() if tag.strip()]
        if len(tag_names) > 5:
            raise ValidationError('Можно указать не более 5 тегов')
        
        for tag_name in tag_names:
            if len(tag_name) > 20:
                raise ValidationError(f'Тег "{tag_name}" слишком длинный (максимум 20 символов)')
            if ' ' in tag_name:
                raise ValidationError(f'Тег "{tag_name}" не должен содержать пробелы')
        
        return tags_str

    def save(self, commit=True, author=None):
        question = super().save(commit=False)
        if author:
            question.author = author
        
        if commit:
            question.save()
            
            tags_str = self.cleaned_data.get('tags', '')
            if tags_str:
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

    def clean_text(self):
        text = self.cleaned_data.get('text')
        if len(text) < 10:
            raise ValidationError('Ответ должен содержать минимум 10 символов')
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