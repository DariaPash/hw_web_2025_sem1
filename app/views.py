from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, JsonResponse
from django.views.decorators.http import require_http_methods
from django.urls import reverse
from django.db.models import Q
try:
    from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
except ImportError:
    SearchVector = None
    SearchQuery = None
    SearchRank = None
from .models import Question, Answer, Tag, QuestionLike, AnswerLike
from .forms import LoginForm, SignupForm, ProfileEditForm, QuestionForm, AnswerForm
from .utils import paginate, prepare_profile_context


def _get_questions_with_pagination(questions_queryset, request, per_page=10):
    questions = questions_queryset.select_related('author').prefetch_related('tags')
    page = paginate(questions, request, per_page=per_page)
    return page


def index(request):
    questions = Question.objects.new()
    page = _get_questions_with_pagination(questions, request)
    
    user_question_likes = {}
    if request.user.is_authenticated:
        question_ids = [q.id for q in page.object_list]
        user_likes = QuestionLike.objects.filter(question_id__in=question_ids, user=request.user)
        user_question_likes = {like.question_id: like for like in user_likes}
    
    return render(request, 'index.html', {
        'page': page, 
        'questions': page.object_list,
        'user_question_likes': user_question_likes,
    })


def hot(request):
    questions = Question.objects.best()
    page = _get_questions_with_pagination(questions, request)
    
    user_question_likes = {}
    if request.user.is_authenticated:
        question_ids = [q.id for q in page.object_list]
        user_likes = QuestionLike.objects.filter(question_id__in=question_ids, user=request.user)
        user_question_likes = {like.question_id: like for like in user_likes}
    
    return render(request, 'hot.html', {
        'page': page, 
        'questions': page.object_list,
        'user_question_likes': user_question_likes,
    })


def tag(request, tag_name):
    tag_obj = get_object_or_404(Tag, name=tag_name)
    questions = Question.objects.by_tag(tag_name)
    page = _get_questions_with_pagination(questions, request)
    
    user_question_likes = {}
    if request.user.is_authenticated:
        question_ids = [q.id for q in page.object_list]
        user_likes = QuestionLike.objects.filter(question_id__in=question_ids, user=request.user)
        user_question_likes = {like.question_id: like for like in user_likes}
    
    return render(request, 'tag.html', {
        'tag_name': tag_name, 
        'page': page, 
        'questions': page.object_list,
        'user_question_likes': user_question_likes,
    })


def question_view(request, question_id):
    question_obj = get_object_or_404(
        Question.objects.select_related('author').prefetch_related('tags'),
        id=question_id
    )
    answers = question_obj.answers.select_related('author').order_by('-is_correct', '-created_at')
    answers_page = paginate(answers, request, per_page=10)
    
    answer_form = AnswerForm()
    
    user_question_like = None
    user_answer_likes = {}
    if request.user.is_authenticated:
        try:
            user_question_like = QuestionLike.objects.get(question=question_obj, user=request.user)
        except QuestionLike.DoesNotExist:
            pass
        
        answer_ids = [answer.id for answer in answers_page.object_list]
        user_likes = AnswerLike.objects.filter(answer_id__in=answer_ids, user=request.user)
        user_answer_likes = {like.answer_id: like for like in user_likes}
    
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect(f"{reverse('login')}?continue={request.path}")
        
        answer_form = AnswerForm(request.POST)
        if answer_form.is_valid():
            answer = answer_form.save(commit=False, question=question_obj, author=request.user)
            answer.save()
            
            from .centrifugo_client import publish_to_centrifugo
            channel = f"question_{question_obj.id}"
            answer_data = {
                'id': answer.id,
                'text': answer.text,
                'author': {
                    'id': answer.author.id,
                    'username': answer.author.username,
                },
                'is_correct': answer.is_correct,
                'likes_cnt': answer.likes_cnt,
                'dislikes_cnt': answer.dislikes_cnt,
                'created_at': answer.created_at.isoformat(),
                'time_ago': answer.get_time_ago(),
            }
            publish_to_centrifugo(channel, answer_data)
            
            all_answers = list(question_obj.answers.select_related('author').order_by('-is_correct', '-created_at'))
            try:
                answer_index = all_answers.index(answer)
                page_number = (answer_index // 10) + 1
            except (ValueError, IndexError):
                page_number = 1
            
            return redirect(f"{question_obj.get_url()}?page={page_number}#answer-{answer.id}")
    
    return render(request, 'question.html', {
        'question': question_obj,
        'answers_page': answers_page,
        'answers': answers_page.object_list,
        'answer_form': answer_form,
        'user_question_like': user_question_like,
        'user_answer_likes': user_answer_likes,
    })


def ask(request):
    if not request.user.is_authenticated:
        return redirect(f"{reverse('login')}?continue={request.path}")
    
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=True, author=request.user)
            return redirect(question.get_url())
    else:
        form = QuestionForm()
    
    return render(request, 'ask.html', {'form': form})


def search(request):
    query = request.GET.get('q', '').strip()
    questions = Question.objects.none()
    
    if query:
        words = query.split()
        if SearchVector and SearchQuery and SearchRank and len(words) > 0:
            try:
                search_vector = SearchVector('title', weight='A') + SearchVector('text', weight='B')
                search_query = SearchQuery(' & '.join(words))
                
                questions = Question.objects.annotate(
                    search=search_vector,
                    rank=SearchRank(search_vector, search_query)
                ).filter(
                    search=search_query
                ).order_by('-rank', '-created_at')
            except Exception:
                questions = Question.objects.filter(
                    Q(title__icontains=query) | Q(text__icontains=query)
                ).order_by('-created_at')
        else:
            questions = Question.objects.filter(
                Q(title__icontains=query) | Q(text__icontains=query)
            ).order_by('-created_at')
    
    page = _get_questions_with_pagination(questions, request)
    
    user_question_likes = {}
    if request.user.is_authenticated:
        question_ids = [q.id for q in page.object_list]
        user_likes = QuestionLike.objects.filter(question_id__in=question_ids, user=request.user)
        user_question_likes = {like.question_id: like for like in user_likes}
    
    return render(request, 'search.html', {
        'query': query,
        'page': page,
        'questions': page.object_list,
        'user_question_likes': user_question_likes,
    })


@require_http_methods(["GET"])
def search_suggestions(request):
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({'suggestions': []})
    
    questions = Question.objects.filter(
        Q(title__icontains=query) | Q(text__icontains=query)
    ).order_by('-created_at')[:5]
    
    suggestions = [
        {
            'id': q.id,
            'title': q.title,
            'url': q.get_url(),
            'preview': q.get_preview(100),
        }
        for q in questions
    ]
    
    return JsonResponse({'suggestions': suggestions})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')
    
    next_url = request.GET.get('continue', None)
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        post_next = request.POST.get('next', next_url)
        if post_next:
            next_url = post_next
            
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                if user.is_active:
                    login(request, user)
                    if next_url:
                        if next_url.startswith('/'):
                            return redirect(next_url)
                        try:
                            return redirect(next_url)
                        except:
                            pass
                    return redirect('index')
                else:
                    form.add_error(None, 'Ваш аккаунт неактивен. Обратитесь к администратору.')
            else:
                form.add_error('password', 'Неверный пароль')
    else:
        form = LoginForm()
    
    return render(request, 'login.html', {'form': form, 'next_url': next_url})


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        form = SignupForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = SignupForm()
    
    return render(request, 'signup.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('index')


@login_required
def profile_edit(request):
    from .models import Profile
    from django.contrib import messages
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = ProfileEditForm(
            request.POST, 
            request.FILES, 
            instance=profile, 
            user=request.user
        )
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('profile_edit')
    else:
        form = ProfileEditForm(instance=profile, user=request.user)
    
    return render(request, 'profile_edit.html', {'form': form, 'user': request.user})


def profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    
    if request.user.is_authenticated and request.user == profile_user and request.method == 'POST':
        from .models import Profile
        from django.contrib import messages
        profile_obj, created = Profile.objects.get_or_create(user=profile_user)
        form = ProfileEditForm(
            request.POST, 
            request.FILES, 
            instance=profile_obj, 
            user=profile_user
        )
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('profile', username=username)
    else:
        form = None
        if request.user.is_authenticated and request.user == profile_user:
            from .models import Profile
            profile_obj, created = Profile.objects.get_or_create(user=profile_user)
            form = ProfileEditForm(instance=profile_obj, user=profile_user)
    
    context = prepare_profile_context(profile_user, request)
    context['settings_form'] = form
    return render(request, 'profile.html', context)


@login_required
@require_http_methods(["POST"])
def question_like(request, question_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Требуется авторизация'}, status=401)
    
    question = get_object_or_404(Question, id=question_id)
    like_type = request.POST.get('type', 'like')
    is_positive = like_type == 'like'
    
    try:
        like = QuestionLike.objects.get(question=question, user=request.user)
        if like.is_positive == is_positive:
            like.delete()
            if is_positive:
                question.likes_cnt = max(0, question.likes_cnt - 1)
            else:
                question.dislikes_cnt = max(0, question.dislikes_cnt - 1)
            question.save(update_fields=['likes_cnt', 'dislikes_cnt'])
        else:
            like.is_positive = is_positive
            like.save()
            if is_positive:
                question.likes_cnt += 1
                question.dislikes_cnt = max(0, question.dislikes_cnt - 1)
            else:
                question.dislikes_cnt += 1
                question.likes_cnt = max(0, question.likes_cnt - 1)
            question.save(update_fields=['likes_cnt', 'dislikes_cnt'])
    except QuestionLike.DoesNotExist:
        QuestionLike.objects.create(question=question, user=request.user, is_positive=is_positive)
        if is_positive:
            question.likes_cnt += 1
        else:
            question.dislikes_cnt += 1
        question.save(update_fields=['likes_cnt', 'dislikes_cnt'])
    
    question.refresh_from_db()
    
    return JsonResponse({
        'rating': question.get_rating(),
        'likes_cnt': question.likes_cnt,
        'dislikes_cnt': question.dislikes_cnt,
    })


@login_required
@require_http_methods(["POST"])
def answer_like(request, answer_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Требуется авторизация'}, status=401)
    
    answer = get_object_or_404(Answer, id=answer_id)
    like_type = request.POST.get('type', 'like')
    is_positive = like_type == 'like'
    
    try:
        like = AnswerLike.objects.get(answer=answer, user=request.user)
        if like.is_positive == is_positive:
            like.delete()
            if is_positive:
                answer.likes_cnt = max(0, answer.likes_cnt - 1)
            else:
                answer.dislikes_cnt = max(0, answer.dislikes_cnt - 1)
            answer.save(update_fields=['likes_cnt', 'dislikes_cnt'])
        else:
            like.is_positive = is_positive
            like.save()
            if is_positive:
                answer.likes_cnt += 1
                answer.dislikes_cnt = max(0, answer.dislikes_cnt - 1)
            else:
                answer.dislikes_cnt += 1
                answer.likes_cnt = max(0, answer.likes_cnt - 1)
            answer.save(update_fields=['likes_cnt', 'dislikes_cnt'])
    except AnswerLike.DoesNotExist:
        AnswerLike.objects.create(answer=answer, user=request.user, is_positive=is_positive)
        if is_positive:
            answer.likes_cnt += 1
        else:
            answer.dislikes_cnt += 1
        answer.save(update_fields=['likes_cnt', 'dislikes_cnt'])
    
    answer.refresh_from_db()
    
    return JsonResponse({
        'rating': answer.get_rating(),
        'likes_cnt': answer.likes_cnt,
        'dislikes_cnt': answer.dislikes_cnt,
    })


@login_required
@require_http_methods(["POST"])
def mark_answer_correct(request, question_id, answer_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Требуется авторизация'}, status=401)
    
    question = get_object_or_404(Question, id=question_id)
    answer = get_object_or_404(Answer, id=answer_id, question=question)
    
    if question.author != request.user:
        return JsonResponse({'error': 'Только автор вопроса может отмечать правильный ответ'}, status=403)
    
    answer.is_correct = not answer.is_correct
    answer.save(update_fields=['is_correct'])
    
    return JsonResponse({
        'is_correct': answer.is_correct,
    })