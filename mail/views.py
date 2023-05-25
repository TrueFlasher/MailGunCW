import os
import requests
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect

from .forms import RegistrationForm
from .models import Email


def send_email(sender, recipient, subject, content):
    domain = os.environ.get('DOMAIN')
    api_key = os.environ.get('API_KEY')
    url = f"https://api.mailgun.net/v3/{domain}/messages"
    auth = ('api', api_key)
    data = {
        'from': sender,
        'to': recipient,
        'subject': subject,
        'text': content
    }

    response = requests.post(url, auth=auth, data=data)

    if response.status_code == 200:
        print('Сообщение успешно отправлено')
    else:
        print('Произошла ошибка при отправке сообщения')


def send_email_view(request):
    if request.method == 'POST':
        sender = request.POST.get('sender')
        recipient = request.POST.get('recipient')
        subject = request.POST.get('subject')
        content = request.POST.get('content')

        send_email(sender, recipient, subject, content)

        return render(request, 'success.html')

    return render(request, 'send_email.html')


def registration(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect('login')
    else:
        form = RegistrationForm()
    return render(request, 'registration.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                # Сохраняем email в сессии
                request.session['email'] = user.email
                return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


def welcome(request):
    return render(request, 'welcome.html')


@login_required




def view_messages(request):
    if request.user.is_authenticated:
        # Получение списка сообщений с помощью Mailgun API
        domain = os.environ.get('DOMAIN')
        api_key = os.environ.get('API_KEY')
        url = f"https://api.mailgun.net/v3/{domain}/events"
        params = {
            'event': 'accepted',  # Укажите необходимые события
            'limit': 5,  # Укажите максимальное количество сообщений для получения
            'to': request.user.email,
        }
        auth = ('api', api_key)
        response = requests.get(url, auth=auth, params=params)
        data = response.json()

        # Обработка и сохранение полученных сообщений в модели Email
        messages = []
        for item in data['items']:
            sender = item['message']['headers'].get('from', '')
            recipient = item['message']['headers'].get('to', '')
            subject = item['message']['headers'].get('subject', '')
            storage_url = item['storage']['url']
            storage_auth = ('api', api_key)
            storage_response = requests.get(storage_url, auth=storage_auth)
            storage_data = storage_response.json()
            content = storage_data['body-plain']

            # Создание объекта Email и сохранение в базе данных
            email = Email.objects.create(
                sender=sender,
                recipient=recipient,
                subject=subject,
                content=content
            )
            messages.append(email)

        return render(request, 'view_messages.html', {'messages': messages})
    else:
        return render(request, 'login.html')


@login_required
def view_sent_messages(request):
    if request.user.is_authenticated:
        # Параметры аутентификации Mailgun API
        domain = os.environ.get('DOMAIN')
        api_key = os.environ.get('API_KEY')

        # Запрос списка отправленных сообщений с помощью Mailgun API
        url = f"https://api.mailgun.net/v3/{domain}/events"
        params = {
            'event': 'delivered',
            'limit': 5,
            'from': request.user.email,
        }
        auth = ('api', api_key)
        response = requests.get(url, auth=auth, params=params)
        data = response.json()

        # Обработка и сохранение полученных сообщений в списке

        sent_messages = []
        for item in data['items']:
            recipient = item['message']['headers'].get('to', '')
            subject = item['message']['headers'].get('subject', '')
            storage_url = item['storage']['url']
            storage_auth = ('api', api_key)
            storage_response = requests.get(storage_url, auth=storage_auth)
            storage_data = storage_response.json()
            content = storage_data['body-plain']



            sent_messages.append({
                'subject': subject,
                'recipient': recipient,
                'content': content,
            })

        return render(request, 'view_sent_messages.html', {'sent_messages': sent_messages})
    else:
        return render(request, 'login.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('welcome')


@login_required
def dashboard(request):
    user = request.user
    email = user.email

    return render(request, 'dashboard.html', {'user': user, 'email': email})
