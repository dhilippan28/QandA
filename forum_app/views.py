from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import RegistrationForm, LoginForm, QuestionForm, AnswerForm
from .models import Question, Tag, Answer, Like, Notification
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Q
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, 'Registration successful! You can now log in.')
            return redirect('login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('list_questions')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            identifier = form.cleaned_data['username']
            password = form.cleaned_data['password']

            # Try to find the user by username or email
            try:
                user_obj = User.objects.get(Q(username=identifier) | Q(email=identifier))
                user = authenticate(username=user_obj.username, password=password)
                if user:
                    login(request, user)
                    messages.success(request, f"Welcome back, {user.username}!")
                    return redirect('list_questions')
                else:
                    messages.error(request, "Incorrect password.")
            except User.DoesNotExist:
                messages.error(request, "Username or email not found.")
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def post_question(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.user = request.user
            question.save()
            tag_names = [name.strip().lower() for name in form.cleaned_data['tags'].split(',') if name.strip()]
            for name in tag_names:
                tag, _ = Tag.objects.get_or_create(name=name)
                question.tags.add(tag)
            return redirect('list_questions')
    else:
        form = QuestionForm()
    return render(request, 'post_question.html', {'form': form})


@login_required
def list_questions(request):
    tag_filters = request.GET.getlist("tag")
    search_query = request.GET.get("search")

    questions = Question.objects.select_related('user').prefetch_related('tags').all().order_by("-created_at")

    if tag_filters:
        questions = questions.filter(tags__name__in=tag_filters).distinct()

    if search_query:
        questions = questions.filter(title__icontains=search_query)

    paginator = Paginator(questions, 10)
    page = request.GET.get('page')
    current_page = paginator.get_page(page)

    tags = Tag.objects.all()

    return render(request, 'list_questions.html', {
        'questions': current_page,
        'page_obj': current_page,
        'tags': tags,
        'selected_tags': tag_filters,
        'search_query': search_query if search_query else '',
    })


@login_required
def question_detail(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    answers = question.answers.select_related('user').prefetch_related('likes__user')

    liked_answer_ids = set(
        Like.objects.filter(user=request.user, answer__question=question)
        .values_list('answer_id', flat=True)
    )

    if request.method == 'POST':
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.user = request.user
            answer.question = question
            answer.save()
            if question.user != request.user:
                # Create a notification for the question owner
                Notification.objects.create(
                    user=question.user,
                    question=question,
                    message=f"{request.user.username} answered your question '{question.title}'"
                )
            messages.success(request, "Your answer has been posted!")
            return redirect('question_detail', question_id=question.id)
    else:
        form = AnswerForm()

    return render(request, 'question_detail.html', {
        'question': question,
        'answers': answers,
        'form': form,
        'liked_answer_ids': liked_answer_ids
    })


@login_required
def like_answer(request, answer_id):
    answer = get_object_or_404(Answer, id=answer_id)

    like, created = Like.objects.get_or_create(user=request.user, answer=answer)
    if not created:
        # Already liked — user wants to unlike
        like.delete()
        messages.info(request, "You unliked the answer.")
    else:
        messages.success(request, "You liked the answer.")

        # Create a notification if the answer belongs to someone else
        if answer.user != request.user:
            Notification.objects.create(
                user=answer.user,
                message=f"{request.user.username} liked your answer.",
                question=answer.question  # assuming the Notification model has a FK to Question
            )
            unread_count = Notification.objects.filter(user=answer.user, is_read=False).count()
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"user_{answer.user.id}",
                {
                    "type": "send_notification",
                    "content": {
                        "message": f"{request.user.username} liked your answer",
                        "data":{ "unread_count": unread_count},
                        "url": f"/questions/{answer.question.id}/"
                    }
                }
            )

    return redirect('question_detail', question_id=answer.question.id)



@login_required
def get_notifications(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    paginator = Paginator(notifications, 10)
    page = request.GET.get('page')
    current_page = paginator.get_page(page)
    return render(request, 'notifications.html', {
        'notifications': current_page,
        'page_obj': current_page
    })

@login_required
def read_notification_redirect(request, notification_id):
    try:
        notification = Notification.objects.get(id=notification_id, user=request.user)
        notification.is_read = True
        notification.save()
        return redirect('question_detail', question_id=notification.question.id)
    except Notification.DoesNotExist:
        return redirect('get_notifications')

